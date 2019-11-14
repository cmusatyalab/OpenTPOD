import React from "react";
import { Dimmer, Page, Grid } from "tabler-react";
import { LabelManagementPanel } from "./Label.react";
import SiteWrapper from "./SiteWrapper.react";
import { fetchJSON } from "./util";
import URI from "urijs";
import { endpoints } from "./url";
import Iframe from "react-iframe";
import windowSize from "react-window-size";

class AnnotatePage extends React.Component {
    state = {
        labels: [],
        loading: true
    };
    taskInfo = null;

    getLabels = () => {
        fetchJSON(
            URI.joinPaths(endpoints.tasks, this.props.match.params.tid),
            "GET"
        ).then(resp => {
            this.taskInfo = resp;
            this.setState({
                labels: resp.labels,
                loading: false
            });
        });
    };

    addLabel = label => {
        const curLabels = this.state.labels.slice(0);
        curLabels.push({
            name: label
        });
        const req = {
            name: this.taskInfo.name,
            labels: curLabels,
            image_quality: this.taskInfo.image_quality
        };
        fetchJSON(
            URI.joinPaths(endpoints.tasks, this.props.match.params.tid),
            "PATCH",
            req
        ).then(() => {
            this.getLabels();
            // force iframe update
            window.location.reload();
        });
    };

    deleteLabel = label => {
        // TODO (junjuew): CVAT doesn't seem to have support for removing label yet.
        const curLabels = this.state.labels.filter(value => {
            return value.name !== label;
        });
        console.log(curLabels);
        const req = {
            name: this.taskInfo.name,
            labels: curLabels,
            image_quality: this.taskInfo.image_quality
        };
        fetchJSON(
            URI.joinPaths(endpoints.tasks, this.props.match.params.tid),
            "PATCH",
            req
        ).then(() => {
            this.getLabels();
        });
    };

    componentDidMount() {
        this.getLabels();
    }

    render() {
        let curHost = window.location.protocol + "//" + window.location.host;
        let cvatURL =
            curHost + "/cvat-ui/?id=" + this.props.match.params.jid.toString();
        return (
            <SiteWrapper>
                <Page.Content
                    title="What do you want to label?"
                    style={{ height: "100%" }}
                >
                    <Grid.Row>
                        <section className="container">
                            {this.state.loading ? (
                                <Dimmer active loader />
                            ) : (
                                <>
                                    <LabelManagementPanel
                                        taskID={this.props.match.params.tid}
                                        labels={this.state.labels}
                                        onAddLabel={this.addLabel}
                                        onDeleteLabel={this.deleteLabel}
                                    />
                                </>
                            )}
                        </section>
                    </Grid.Row>
                </Page.Content>
                {!this.state.loading && this.state.labels.length !== 0 && (
                    <Iframe
                        url={cvatURL}
                        width={this.props.windowWidth}
                        height={0.8 * this.props.windowWidth}
                        id="cvat-iframe"
                    />
                )}
            </SiteWrapper>
        );
    }
}

export default windowSize(AnnotatePage);
