// @flow

// Import the Image EXIF Orientation and Image Preview plugins
// Note: These need to be installed separately
// import FilePondPluginImageExifOrientation from "filepond-plugin-image-exif-orientation";
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
// Import FilePond styles
import "filepond/dist/filepond.min.css";
import React from 'react';
// Import React FilePond
import { FilePond, registerPlugin } from "react-filepond";
import { Button, Card, Dimmer, Grid, Page } from "tabler-react";
import ReactPlayer from "react-player";
import SiteWrapper from "./SiteWrapper.react";
import { fetchJSON } from "./util";
import { endpoints } from "./url";
import "./VideoPage.css";

registerPlugin(FilePondPluginFileValidateType);

class VideoPage extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            files: [],
            videoInfos: [],
            loading: true
        };

        this.fetchVideoInfo = this.fetchVideoInfo.bind(this);
    }

    fetchVideoInfo() {
        fetchJSON(endpoints.tasks, "GET").then(
            resp => {
                this.setState({
                    videoInfos: resp,
                    loading: false
                });
            }
        );
    }


    componentDidMount() {
        this.fetchVideoInfo();
    }

    render() {
        let videoInfoCards = <Grid.Row> {this.state.videoInfos.map(
            (item, index) =>
                <Grid.Col md={4} key={index}>
                    <Card>
                        <Card.Header>
                            <Card.Title>{item.name.replace(/(.{10})/g, "$1\n")}</Card.Title>
                            <Card.Options>
                                <Button
                                    outline
                                    RootComponent="button"
                                    color="primary"
                                    size="sm"
                                    icon="tag"
                                    onClick={
                                        (e) => {
                                            e.preventDefault();
                                            this.props.history.push('/label/' + item.id)
                                        }
                                    }
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
                                    onClick={
                                        (e) => {
                                            fetchJSON(
                                                endpoints.tasks + "/" + item.id,
                                                "DELETE").then(this.setState(
                                                    {
                                                        videoInfos: this.state.videoInfos.filter(
                                                            (_, i) => i !== index
                                                        )
                                                    }
                                                ))
                                        }}
                                >
                                    Delete
                                </Button>
                            </Card.Options>
                        </Card.Header>
                        <Card.Body>
                            {item.loading ? <div>
                                The video is being processed...<Dimmer active loader />
                            </div> : <div>
                                    <ReactPlayer
                                        url={endpoints.mediaData + item.id + "/.upload/" + item.name}
                                        width="100%"
                                        height="100%"
                                        controls={true}
                                        light={endpoints.tasks + '/' + item.id + "/frames/0"}
                                    />
                                </div>}
                        </Card.Body>
                    </Card>
                </Grid.Col >
        )}
        </Grid.Row>

        return (
            <SiteWrapper>
                <Page.Content>
                    <Grid.Row>
                        <section className="container">
                            <FilePond
                                ref={ref => (this.pond = ref)}
                                labelIdle="Drag & Drop videos or Click to Browse."
                                files={this.state.files}
                                allowMultiple={true}
                                server={{
                                    process: (fieldName, file, metadata, load, error, progress, abort) => {
                                        // create CVAT task first
                                        let data = {
                                            'name': file.name,
                                            'labels': [],
                                            'image_quality': 100
                                        }
                                        fetchJSON(endpoints.tasks, 'POST', data).then(
                                            resp => {
                                                // fieldName is the name of the input field
                                                // file is the actual file object to send
                                                console.log(resp);
                                                debugger;
                                                const batchOfFiles = new FormData();
                                                batchOfFiles.append('client_files[0]', file);
                                                const request = new XMLHttpRequest();
                                                request.open('POST', endpoints.tasks + "/" + resp["id"] + "/data");
                                                // Should call the progress method to update the progress to 100% before calling load
                                                // Setting computable to false switches the loading indicator to infinite mode
                                                request.upload.onprogress = (e) => {
                                                    progress(e.lengthComputable, e.loaded, e.total);
                                                };
                                                // Should call the load method when done and pass the returned server file id
                                                // this server file id is then used later on when reverting or restoring a file
                                                // so your server knows which file to return without exposing that info to the client
                                                request.onload = function () {
                                                    if (request.status >= 200 && request.status < 300) {
                                                        // the load method accepts either a string (id) or an object
                                                        load(request.responseText);
                                                    }
                                                    else {
                                                        // Can call the error method if something is wrong, should exit after
                                                        error('oh no');
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
                                            }
                                        ).catch(
                                            e => {
                                                console.error(e);
                                                error(e)
                                                abort();
                                            }
                                        );
                                    },

                                    fetch: null,
                                    revert: null,
                                    load: null,
                                }}
                                allowRevert={false}
                                acceptedFileTypes="video/*"
                                fileValidateTypeLabelExpectedTypes='Expects a video file'
                                onupdatefiles={fileItems => {
                                    // Set currently active file objects to this.state
                                    this.setState({
                                        files: fileItems.map(fileItem => fileItem.file)
                                    });
                                }}
                                onprocessfiles={
                                    () => {
                                        this.setState({ files: [] });
                                        this.fetchVideoInfo();
                                    }
                                }
                            />
                        </section>
                    </Grid.Row>
                    {
                        (this.state.loading) ?
                            <Dimmer active loader /> : videoInfoCards
                    }
                </Page.Content>
            </SiteWrapper >
        );
    }
}
export default VideoPage;
