import SiteWrapper from "./SiteWrapper.react";
import { endpoints, PAGE_SIZE } from "./const";
import {
    downloadByPoll as checkDownload,
    fetchJSON,
    lineWrap,
    clamp
} from "./util";

import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { Button, Card, Dimmer, Form, Grid, Page } from "tabler-react";
import URI from "urijs";

import "./App.css";
import { PaginatedInfoCardList } from "./CardPageTemplateForModel.react";

import { NewDetectorForm } from "./LoadModelForm.react";

const fetchModel = id => {
    /* Get model json from backend*/
    let url = URI.joinPaths(endpoints.detectormodels, id);
    return fetchJSON(url, "GET");
};

const makeModelCardOptions = ({ resourceObj, onDelete }) => {
    let history = useHistory();
    return (
        <>

            <Button
                outline
                RootComponent="button"
                color="danger"
                size="sm"
                icon="trash"
                method="delete"
                onClick={e => {
                    fetchJSON(
                        URI.joinPaths(
                            endpoints.detectormodels,
                            resourceObj.id.toString()
                        ),
                        "DELETE"
                    ).then(onDelete);
                }}
            >
                Delete
            </Button>
        </>
    );
};

const makeModelTitle = resourceObj => {
    return lineWrap(resourceObj.id.toString());
};

const makeModelCardBody = ({ resourceObj }) => {
    return (
        <>
            {/* <b>Status:</b> {resourceObj.name} <br /> */}
            <b>Created Date:</b> {resourceObj.created_date} <br />
        </>
    );
};

const LoadModelPage = ({ ...props }) => {
    let history = useHistory();
    const [models, setModels] = useState(null);
    const [curPage, setCurPage] = useState(null);

    const loadModels = newPage => {
        if (models !== null)
            newPage = clamp(newPage, 1, Math.ceil(models.count / PAGE_SIZE));
        setModels(null);
        let url = new URI(endpoints.detectormodels);
        url.setSearch("page", newPage);
        fetchJSON(url, "GET").then(resp => {
            setModels(resp);
            setCurPage(newPage);
        });
    };

    useEffect(() => {
        loadModels(1);
    }, []);

    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header title="Load Model">
                    <Grid.Col width={1} offset={6}>
                        <Button
                            outline
                            RootComponent="button"
                            color="primary"
                            size="md"
                            icon="plus"
                            onClick={e => {
                                e.preventDefault();
                                history.push(endpoints.uiModelNew);
                            }}
                        >
                            Create
                        </Button>
                    </Grid.Col>
                    <Grid.Col>
                        <Form.Input icon="search" placeholder="Search" />
                    </Grid.Col>
                </Page.Header>
                {models == null ? (
                    <Dimmer active loader />
                ) : (
                    <PaginatedInfoCardList
                        iterableResourceObjs={models.results}
                        pageCount={Math.ceil(models.count / PAGE_SIZE)}
                        makeTitle={makeModelTitle}
                        Options={makeModelCardOptions}
                        makeBody={resourceObj =>
                            makeModelCardBody({
                                resourceObj: resourceObj
                            })
                        }
                        forcePage={curPage - 1}
                        onPageChange={data => {
                            let newPage = data.selected + 1;
                            loadModels(newPage);
                        }}
                        onDelete={() => {
                            let page = curPage;
                            if (models !== null)
                                page = clamp(
                                    curPage,
                                    1,
                                    Math.ceil((models.count - 1) / PAGE_SIZE)
                                );
                            loadModels(page);
                        }}
                    />
                )}
            </Page.Content>
        </SiteWrapper>
    );
};

const ModelNewPage = ({ ...props }) => {
    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header title="Load New Model"></Page.Header>
                <Grid>
                    <NewDetectorForm {...props} />
                </Grid>
            </Page.Content>
        </SiteWrapper>
    );
};


export { LoadModelPage,ModelNewPage };
