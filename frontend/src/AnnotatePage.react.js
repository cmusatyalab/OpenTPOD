import React, { useEffect, useState } from "react";
import Iframe from "react-iframe";
import Select from "react-select";
import windowSize from "react-window-size";
import { Dimmer, Grid, Page, Header } from "tabler-react";
import URI from "urijs";
import { endpoints, reactSelectTablerStyles } from "./const";
import { LabelManagementPanel } from "./Label.react";
import SiteWrapper from "./SiteWrapper.react";
import { fetchJSON } from "./util";

const AnnotatePage = ({ ...props }) => {
    const [task, setTask] = useState(null);
    const [segment, setSegment] = useState(null);

    const loadTask = () => {
        setTask(null);
        fetchJSON(
            URI.joinPaths(endpoints.tasks, props.match.params.tid),
            "GET"
        ).then(resp => {
            setTask(resp);
        });
    };

    const addLabel = label => {
        let newLabel = {
            name: label
        };
        let newLabelList = [...task.labels, newLabel];
        const req = {
            name: task.name,
            labels: newLabelList,
            image_quality: task.image_quality
        };
        fetchJSON(
            URI.joinPaths(endpoints.tasks, props.match.params.tid),
            "PATCH",
            req
        ).then(() => {
            loadTask();
            // force iframe update
            window.location.reload();
        });
    };

    const deleteLabel = label => {
        // TODO (junjuew): CVAT doesn't seem to have support for removing label yet.
        const newLabelList = task.labels.filter(value => {
            return value.name !== label;
        });
        const req = {
            name: task.name,
            labels: newLabelList,
            image_quality: task.image_quality
        };
        fetchJSON(
            URI.joinPaths(endpoints.tasks, props.match.params.tid),
            "PATCH",
            req
        ).then(() => {
            loadTask();
        });
    };

    useEffect(() => {
        loadTask();
    }, []);

    let curHost = window.location.protocol + "//" + window.location.host;
    return (
        <SiteWrapper>
            <Page.Content title="Annotate" style={{ height: "100%" }}>
                {task == null ? (
                    <Dimmer active loader />
                ) : (
                    <>
                        <Grid>
                            <Grid.Row>
                                <LabelManagementPanel
                                    taskID={props.match.params.tid}
                                    labels={task.labels}
                                    onAddLabel={addLabel}
                                    onDeleteLabel={deleteLabel}
                                />
                            </Grid.Row>
                            <hr />
                            <Grid.Row>
                                <Grid.Col>
                                    <p>Choose a Video Segment To Label</p>
                                    <Select
                                        name="Select Segment"
                                        styles={reactSelectTablerStyles}
                                        options={task.segments.map(
                                            (segment, index) => {
                                                // TODO (junjuew): double check with
                                                // CVAT to see if it is possible to have
                                                // multiple jobs per segment
                                                return {
                                                    value: segment.jobs[0].id.toString(),
                                                    label: index.toString()
                                                };
                                            }
                                        )}
                                        value={segment}
                                        isLoading={task == null}
                                        isSearchable={true}
                                        onChange={selectedOption => {
                                            setSegment(selectedOption);
                                        }}
                                    />
                                </Grid.Col>
                            </Grid.Row>
                        </Grid>
                    </>
                )}
            </Page.Content>
            {segment != null && (
                <Iframe
                    url={URI.joinPaths(curHost, "/cvat-ui").setSearch(
                        "id",
                        segment.value
                    )}
                    width={props.windowWidth}
                    height={0.8 * props.windowWidth}
                    id="cvat-iframe"
                />
            )}
        </SiteWrapper>
    );
};

export default windowSize(AnnotatePage);
