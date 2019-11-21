// Import the Image EXIF Orientation and Image Preview plugins
// Note: These need to be installed separately
// import FilePondPluginImageExifOrientation from "filepond-plugin-image-exif-orientation";
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
// Import FilePond styles
import "filepond/dist/filepond.min.css";
import React from 'react';
// Import React FilePond
import { FilePond, registerPlugin } from "react-filepond";
import ReactPlayer from "react-player";
import { Button, Card, Dimmer, Grid, Page } from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import { fetchJSON } from "./util";
import "./VideoPage.css";

registerPlugin(FilePondPluginFileValidateType);

class TrainPage extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            files: [],
            videoInfos: [],
            loading: true
        };

        this.fetchVideoInfo = this.fetchVideoInfo.bind(this);
    }

    handleInit() {
        console.log("FilePond instance has initialised", this.pond);
    }

    fetchVideoInfo() {
        fetchJSON("/api/videos", "GET").then(
            resp => {
                console.log(resp);
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
                            <Card.Title>{item.slug}</Card.Title>
                            <Card.Options>
                                <Button
                                    outline
                                    RootComponent="form"
                                    color="primary"
                                    size="sm"
                                    icon="tag"
                                    href="/label"
                                >
                                    Label
                                </Button>
                                <Button
                                    outline
                                    RootComponent="button"
                                    color="danger"
                                    size="sm"
                                    icon="trash"
                                    action={"/api/video/" + item.id}
                                    method="delete"
                                    onClick={
                                        (e) => {
                                            fetchJSON(
                                                "/api/videos/" + item.id,
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
                                        url={"/api/videos/" + item.id + "/raw"}
                                        width="100%"
                                        height="100%"
                                        controls={true}
                                        light={"/api/videos/" + item.id + "/thumbnail"}
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
                                // maxFiles={3}
                                server={{
                                    process: "./api/videos",
                                    fetch: null,
                                    revert: null,
                                    load: null,
                                }}
                                allowRevert={false}
                                acceptedFileTypes="video/*"
                                fileValidateTypeLabelExpectedTypes='Expects a video file'
                                oninit={() => this.handleInit()}
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
export default TrainPage;
