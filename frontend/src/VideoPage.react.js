// Import the Image EXIF Orientation and Image Preview plugins
// Note: These need to be installed separately
// import FilePondPluginImageExifOrientation from "filepond-plugin-image-exif-orientation";
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";
// Import FilePond styles
import "filepond/dist/filepond.min.css";
import React, { useEffect, useState } from "react";
import { FilePond, registerPlugin } from "react-filepond";
import ReactPlayer from "react-player";
import { useHistory } from "react-router-dom";
import { Button, Dimmer, Grid, Page } from "tabler-react";
import URI from "urijs";
import { PaginatedInfoCardList } from "./CardPageTemplate.react.js";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints } from "./url";
import { fetchJSON, lineWrap } from "./util";
import "./VideoPage.css";

registerPlugin(FilePondPluginFileValidateType);

const makeVideoCardTitle = resourceObj => {
    return lineWrap(resourceObj.name);
};

const makeVideoCardOptions = ({ resourceObj, onDelete }) => {
    let history = useHistory();
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
                            endpoints.uiAnnotate,
                            "tasks",
                            resourceObj.id.toString(),
                            "jobs",
                            resourceObj.segments[0].jobs[0].id.toString()
                        ).toString()
                    ); // only considered 1st job
                }}
            >
                Label
            </Button>
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
                            endpoints.tasks,
                            resourceObj.id.toString()
                        ),
                        "DELETE"
                    ).then(onDelete());
                }}
            >
                Delete
            </Button>
        </>
    );
};

const makeVideoCardBody = resourceObj => {
    return resourceObj.loading ? (
        <div>
            The video is being processed...
            <Dimmer active loader />
        </div>
    ) : (
        <div>
            <ReactPlayer
                url={URI.joinPaths(
                    endpoints.mediaData,
                    resourceObj.id.toString(),
                    ".upload",
                    resourceObj.name
                )}
                width="100%"
                height="100%"
                controls={true}
                light={URI.joinPaths(
                    endpoints.tasks,
                    resourceObj.id.toString(),
                    "/frames/0"
                ).toString()} // expects string type
            />
        </div>
    );
};

const VideoPage = ({ ...props }) => {
    let history = useHistory();
    // in this class, a video is used as the equivalent of a CVAT tasks
    // as CVAT only allows a single video in a task
    const [videos, setVideos] = useState(null);
    const [files, setFiles] = useState([]);

    // fetch task/video information
    const loadVideos = () => {
        fetchJSON(endpoints.tasks, "GET").then(resp => {
            setVideos(resp);
        });
    };

    useEffect(() => {
        loadVideos();
    }, []);

    // called when a new task/video has finished creation
    const onTaskCreated = () => {
        setVideos(null);
        // TODO(junjuew): hacky. delaying video
        // information fetching for a few second to
        // give server some time to extract frames
        // this way, when going to the labeling
        // page, at least some frames are available.
        // the correct way is to get a method that
        // is able to retrieve the information about whether the extraction
        // process has finished or not.
        setTimeout(loadVideos, 10000);
    };

    const createTask = ({
        data,
        onTaskCreated,
        file,
        progress,
        load,
        error,
        abort
    }) => {
        fetchJSON(endpoints.tasks, "POST", data)
            .then(resp => {
                // fieldName is the name of the input field
                // file is the actual file object to send
                const batchOfFiles = new FormData();
                batchOfFiles.append("client_files[0]", file);
                const request = new XMLHttpRequest();
                request.open(
                    "POST",
                    URI.joinPaths(endpoints.tasks, resp.id.toString(), "data")
                );
                // Should call the progress method to update the progress to 100% before calling load
                // Setting computable to false switches the loading indicator to infinite mode
                request.upload.onprogress = e => {
                    progress(e.lengthComputable, e.loaded, e.total);
                };
                // Should call the load method when done and pass the returned server file id
                // this server file id is then used later on when reverting or restoring a file
                // so your server knows which file to return without exposing that info to the client
                request.onload = function() {
                    if (request.status >= 200 && request.status < 300) {
                        // the load method accepts either a string (id) or an object
                        load(request.responseText);
                        onTaskCreated();
                    } else {
                        // Can call the error method if something is wrong, should exit after
                        error("File Upload Failed");
                        abort();
                    }
                };
                request.send(batchOfFiles);
                // Should expose an abort method so the request can be cancelled
                return {
                    abort: () => {
                        // This function is entered if the user has tapped the cancel button
                        request.abort();
                        // Let FilePond know the request has been cancelled
                        abort();
                    }
                };
            })
            .catch(e => {
                console.error(e);
                error(e);
                abort();
            });
    };

    return (
        <SiteWrapper>
            <Page.Content>
                <Grid.Row>
                    <section className="container">
                        <FilePond
                            labelIdle="Drag & Drop videos or Click to Browse."
                            files={files}
                            allowMultiple={true}
                            server={{
                                process: (
                                    fieldName,
                                    file,
                                    metadata,
                                    load,
                                    error,
                                    progress,
                                    abort
                                ) => {
                                    // create CVAT task first
                                    let data = {
                                        name: file.name,
                                        labels: [],
                                        image_quality: 100
                                    };
                                    createTask({
                                        data,
                                        onTaskCreated,
                                        file,
                                        progress,
                                        load,
                                        error,
                                        abort
                                    });
                                },

                                fetch: null,
                                revert: null,
                                load: null
                            }}
                            allowRevert={false}
                            acceptedFileTypes="video/*"
                            fileValidateTypeLabelExpectedTypes="Expects a video file"
                            onupdatefiles={fileItems => {
                                // Set currently active file objects
                                setFiles(
                                    fileItems.map(fileItem => fileItem.file)
                                );
                            }}
                            onprocessfiles={() => {
                                setFiles([]);
                            }}
                        />
                    </section>
                </Grid.Row>
                {videos == null ? (
                    <Dimmer active loader />
                ) : (
                    <PaginatedInfoCardList
                        iterableResourceObjs={videos.results}
                        onPageChange={() => {}}
                        pageCount={Math.ceil(
                            videos.count / videos.results.length
                        )}
                        makeTitle={makeVideoCardTitle}
                        makeOptions={resourceObj =>
                            makeVideoCardOptions({
                                resourceObj: resourceObj,
                                onDelete: () => {
                                    setVideos(null);
                                    // TODO(junjuew): somehow without delays
                                    // information fetched would still
                                    // contain the deleted item
                                    setTimeout(loadVideos, 1000);
                                }
                            })
                        }
                        makeBody={makeVideoCardBody}
                    />
                )}
            </Page.Content>
        </SiteWrapper>
    );
};
export default VideoPage;
