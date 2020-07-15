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
import { PaginatedInfoCardList } from "./CardPageTemplateForData.react.js";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints, PAGE_SIZE, session_storage_key } from "./const";
import { fetchJSON, lineWrap, clamp } from "./util";
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
                    ).then(onDelete);
                }}
            >
                Delete
            </Button>
        </>
    );
};

const VideoCardBody = ({ resourceObj }) => {
    const [status, setStatus] = useState(null);

    // get video status: one of [Queued, Started, Finished, Failed]
    const loadStatus = () => {
        setStatus(null);
        let url = URI.joinPaths(resourceObj.url, "/status").toString();
        // console.log(url)
        fetchJSON(url, "GET").then(resp => {
            setStatus(resp);
            if (resp.state === "Queued" || resp.state === "Started")
                setTimeout(loadStatus, 10000);
        });
    };

    useEffect(() => {
        loadStatus();
    }, []);

    // return status && status.state === "Finished" ? (
        
    return (
        <div>
            <b>Created Date:</b> {resourceObj.created_date} <br />
        </div>);
        
    
    // ) : status && status.state === "Failed" ? (
    //     <div>
    //         <b>Error:</b> Failed to extract the video into images.
    //         <br />
    //     </div>
    // ) : (
    //     <div>
    //         The video is being processed...
    //         <Dimmer active loader />
    //     </div>
    // );
};

const DataPage = ({ ...props }) => {
    // in this class, a video is used as the equivalent of a CVAT tasks
    // as CVAT only allows a single video in a task
    const [videos, setVideos] = useState(null);
    const [files, setFiles] = useState([]);
    const [curPage, setCurPage] = useState(null);

    // fetch task/video information
    const loadVideos = newPage => {
        setVideos(null);
        let url = new URI(endpoints.tasks);
        url.setSearch("page", newPage);
        fetchJSON(url, "GET").then(resp => {
            setVideos(resp);
            setCurPage(newPage);
        });
        // console.log(url)
    };
    
    // console.log(videos)

    useEffect(() => {
        loadVideos(1);
    }, []);

    // called when a new task/video has finished creation
    const onTaskCreated = () => {
        setVideos(null);
        loadVideos(curPage);
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
                // console.log(endpoints.tasks)
                // console.log(resp.id.toString())
                // Should call the progress method to update the progress to 100% before calling load
                // Setting computable to false switches the loading indicator to infinite mode
                request.upload.onprogress = e => {
                    progress(e.lengthComputable, e.loaded, e.total);
                };
                // Should call the load method when done and pass the returned server file id
                // this server file id is then used later on when reverting or restoring a file
                // so your server knows which file to return without exposing
                // that info to the client
                // this is called when the request transaction is finished
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
                            labelIdle="Drag & Drop files or Click to Browse."
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
                                    let userId = sessionStorage.getItem(
                                        session_storage_key.userId
                                    );
                                    
                                    let data = {
                                        name: file.name,
                                        labels: [],
                                        image_quality: 100,
                                        owner: userId,
                                        assignee: userId
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
                            allowFileTypeValidation={false}
                            acceptedFileTypes={[".tfrecord", ".pbtxt"]}
                            // fileValidateTypeLabelExpectedTypes="Expects a tfrecord file"
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
                        pageCount={Math.ceil(videos.count / PAGE_SIZE)}
                        makeTitle={makeVideoCardTitle}
                        makeOptions={resourceObj =>
                            makeVideoCardOptions({
                                resourceObj: resourceObj,
                                onDelete: () => {
                                    let page = curPage;
                                    if (videos !== null)
                                        page = clamp(
                                            curPage,
                                            1,
                                            Math.ceil(
                                                (videos.count - 1) / PAGE_SIZE
                                            )
                                        );
                                    loadVideos(page);
                                }
                            })
                        }
                        Body={VideoCardBody}
                        // react-pagination start from 0
                        // django pagination start from 1
                        // hence the -1/+1
                        forcePage={curPage - 1}
                        onPageChange={data => {
                            let newPage = data.selected + 1;
                            loadVideos(newPage);
                        }}
                    />
                )}
            </Page.Content>
        </SiteWrapper>
    );
};
export default DataPage;
