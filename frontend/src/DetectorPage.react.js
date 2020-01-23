import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { Button, Card, Dimmer, Form, Grid, Page } from "tabler-react";
import URI from "urijs";
import "./App.css";
import { PaginatedInfoCardList } from "./CardPageTemplate.react.js";
import { NewDetectorForm } from "./DetectorForm.react";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints, PAGE_SIZE } from "./const";
import {
    downloadByPoll as checkDownload,
    fetchJSON,
    lineWrap,
    clamp
} from "./util";

const fetchDetector = id => {
    /* Get detector json from backend*/
    let url = URI.joinPaths(endpoints.detectors, id);
    return fetchJSON(url, "GET");
};

const makeDetectorCardTitle = resourceObj => {
    return lineWrap(resourceObj.name);
};

const DetectorCardOptions = ({ resourceObj, onDownload, onDelete }) => {
    const [downloading, setDownloading] = useState(false);

    let history = useHistory();
    let downloadUrl = URI.joinPaths(
        endpoints.detectors,
        resourceObj.id.toString(),
        endpoints.detectorDownloadField
    );
    return (
        <>
            <Button
                outline
                RootComponent="button"
                color="primary"
                size="sm"
                icon="tag"
                onClick={e => {
                    e.preventDefault();
                    history.push(
                        URI.joinPaths(
                            endpoints.uiDetector,
                            resourceObj.id.toString()
                        ).toString()
                    );
                }}
            >
                Details
            </Button>
            {resourceObj.status === "trained" && !downloading && (
                <Button
                    outline
                    color="info"
                    size="sm"
                    icon="download"
                    onClick={e => {
                        e.preventDefault();
                        setDownloading(true);
                        onDownload({
                            downloadUrl: downloadUrl,
                            onDownloadSuccess: () => {
                                setDownloading(false);
                            }
                        });
                    }}
                ></Button>
            )}
            {resourceObj.status === "trained" && downloading && (
                <Button loading color="info" size="sm"></Button>
            )}
            <Button
                outline
                RootComponent="button"
                color="danger"
                size="sm"
                icon="trash"
                method="delete"
                onClick={e => {
                    e.preventDefault();
                    fetchJSON(
                        URI.joinPaths(
                            endpoints.detectors,
                            resourceObj.id.toString()
                        ),
                        "DELETE"
                    ).then(onDelete);
                }}
            ></Button>
        </>
    );
};

const makeDetectorCardBody = ({ resourceObj }) => {
    return (
        <>
            <b>Status:</b> {resourceObj.status} <br />
            <b>Created Date:</b> {resourceObj.created_date} <br />
            <b>Updated Date:</b> {resourceObj.updated_date} <br />
        </>
    );
};

// detailed detector view with all of its field
const DetectorDetailCard = ({ detector }) => {
    return (
        <Card>
            <Card.Header>
                <Card.Title>{lineWrap(detector.name)}</Card.Title>
                <Card.Options>
                    <Button
                        outline
                        RootComponent="button"
                        color="success"
                        size="sm"
                        icon="tag"
                        onClick={e => {
                            e.preventDefault();
                            let url = URI.joinPaths(
                                endpoints.detectors,
                                detector.id.toString(),
                                endpoints.detectorVisualizationField
                            );
                            window.open(url, "_blank");
                        }}
                    >
                        Visualize
                    </Button>
                </Card.Options>
            </Card.Header>
            <Card.Body>
                <b>Status:</b> {detector.status} <br />
                <b>DNN Type:</b> {detector.dnn_type} <br />
                <b>Created Date:</b> {detector.created_date} <br />
                <b>Updated Date:</b> {detector.updated_date} <br />
                <b>Training Set:</b>
                <pre id="json">
                    {" "}
                    {JSON.stringify(detector.train_set, undefined, 2)}{" "}
                </pre>
                <br />
                <b>Training Config:</b>
                <pre id="json">
                    {" "}
                    {JSON.stringify(
                        JSON.parse(detector.train_config),
                        undefined,
                        2
                    )}{" "}
                </pre>
                <br />
            </Card.Body>
        </Card>
    );
};

const DetectorPage = ({ ...props }) => {
    let history = useHistory();
    const [detectors, setDetectors] = useState(null);
    const [curPage, setCurPage] = useState(null);

    const loadDetectors = newPage => {
        if (detectors !== null)
            newPage = clamp(newPage, 1, Math.ceil(detectors.count / PAGE_SIZE));
        setDetectors(null);
        let url = new URI(endpoints.detectors);
        url.setSearch("page", newPage);
        fetchJSON(url, "GET").then(resp => {
            setDetectors(resp);
            setCurPage(newPage);
        });
    };

    useEffect(() => {
        loadDetectors(1);
    }, []);

    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header title="Detectors">
                    <Grid.Col width={1} offset={6}>
                        <Button
                            outline
                            RootComponent="button"
                            color="primary"
                            size="md"
                            icon="plus"
                            onClick={e => {
                                e.preventDefault();
                                history.push(endpoints.uiDetectorNew);
                            }}
                        >
                            Create
                        </Button>
                    </Grid.Col>
                    <Grid.Col>
                        <Form.Input icon="search" placeholder="Search" />
                    </Grid.Col>
                </Page.Header>
                {detectors == null ? (
                    <Dimmer active loader />
                ) : (
                    <PaginatedInfoCardList
                        iterableResourceObjs={detectors.results}
                        pageCount={Math.ceil(detectors.count / PAGE_SIZE)}
                        makeTitle={makeDetectorCardTitle}
                        Options={DetectorCardOptions}
                        makeBody={resourceObj =>
                            makeDetectorCardBody({
                                resourceObj: resourceObj
                            })
                        }
                        forcePage={curPage - 1}
                        onPageChange={data => {
                            let newPage = data.selected + 1;
                            loadDetectors(newPage);
                        }}
                        onDownload={({
                            downloadUrl,
                            onDownloadSuccess = () => {},
                            onDownloadFailure = () => {}
                        }) => {
                            fetchJSON(downloadUrl, "POST").then(() => {
                                // need to continuously fetch the server
                                checkDownload(
                                    downloadUrl,
                                    10000,
                                    1200000,
                                    resp => {
                                        // a workaround to download a link automatically
                                        const link = document.createElement(
                                            "a"
                                        );
                                        link.href = downloadUrl;
                                        link.click();
                                        onDownloadSuccess();
                                    },
                                    onDownloadFailure
                                );
                            });
                        }}
                        onDelete={() => {
                            let page = curPage;
                            if (detectors !== null)
                                page = clamp(
                                    curPage,
                                    1,
                                    Math.ceil((detectors.count - 1) / PAGE_SIZE)
                                );
                            loadDetectors(page);
                        }}
                    />
                )}
            </Page.Content>
        </SiteWrapper>
    );
};

const DetectorDetailPage = ({ props }) => {
    /* Detailed Page for Detectors*/
    const [detector, setDetector] = useState(null);

    let { id } = useParams();
    let history = useHistory();

    const loadResource = () => {
        setDetector(null);
        fetchDetector(id).then(detector => {
            setDetector(detector);
        });
    };

    useEffect(() => {
        loadResource();
    }, []);

    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header
                    title="Detector"
                    options={
                        <Button
                            outline
                            RootComponent="button"
                            color="primary"
                            size="md"
                            onClick={e => {
                                e.preventDefault();
                                history.goBack();
                            }}
                        >
                            Back
                        </Button>
                    }
                ></Page.Header>
                {detector == null ? (
                    <Dimmer active loader />
                ) : (
                    <Grid>
                        <Grid.Row>
                            <DetectorDetailCard detector={detector} />
                        </Grid.Row>
                    </Grid>
                )}
            </Page.Content>
        </SiteWrapper>
    );
};

const DetectorNewPage = ({ ...props }) => {
    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header title="New Detector"></Page.Header>
                <Grid>
                    <NewDetectorForm {...props} />
                </Grid>
            </Page.Content>
        </SiteWrapper>
    );
};

export { DetectorPage, DetectorDetailPage, DetectorNewPage };
