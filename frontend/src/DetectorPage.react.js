import React, { useState, useEffect } from "react";
import URI from "urijs";
import ReactPaginate from "react-paginate";
import { Button, Card, Dimmer, Grid, Page, List, Form } from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints } from "./url";
import { fetchJSON, lineWrap } from "./util";
import "./App.css";

// detector card to display detector information
const DetectorCard = (detector) => {
    return (
        <Card>
            <Card.Header>
                <Card.Title>{lineWrap(detector.name)}</Card.Title>
                <Card.Options>
                    <Button
                        outline
                        RootComponent="button"
                        color="primary"
                        size="sm"
                        icon="tag"
                        onClick={e => {
                            e.preventDefault();
                            this.props.history.push(
                                URI.joinPaths(
                                    endpoints.annotate,
                                    "tasks",
                                    detector.id.toString(),
                                    "jobs",
                                    detector.segments[0].jobs[0].id.toString()
                                ).toString()
                            ); // only consider 1st job
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
                                URI.joinPaths(endpoints.tasks, detector.id.toString()),
                                "DELETE"
                            ).then(
                                // this.setState({
                                //     videoInfos: this.state.videoInfos.filter(
                                //         (_, i) => i !== index
                                //     )
                                // })
                            );
                        }}
                    >
                        Delete
                  </Button>
                </Card.Options>
            </Card.Header>
            <Card.Body>
                {detector.loading ? (
                    <div>
                        The video is being processed...
                    <Dimmer active loader />
                    </div>
                ) : (
                        <div>
                        </div>
                    )}
            </Card.Body>
        </Card>
    )
}

// separate out to a different file
const paginator = () => {

}

const DetectorPage = ({ name }) => {
    // const [loadDetectors, reloadDetectors] = useState(true);
    const [detectors, setDetectors] = useState(null);

    const loadDetectors = () => {
        fetchJSON(endpoints.detectors, "GET").then(resp => {
            console.log("detectors: " + resp);
            setDetectors(resp);
        });
    }

    useEffect(() => {
        loadDetectors()
    }, [])

    return (
        <SiteWrapper>
            <Page.Content>
                <Page.Header
                    title="Detectors"
                    options={<Form.Input icon="search" placeholder="Search" />}
                >
                </Page.Header>
                {detectors == null ? <Dimmer active loader /> :
                    <Grid.Row>
                        <ReactPaginate
                            previousLabel={"<"}
                            nextLabel={">"}
                            breakLabel={"..."}
                            pageCount={Math.ceil(
                                detectors.count / detectors.results.length)}
                            marginPagesDisplayed={1}
                            pageRangeDisplayed={2}
                            // onPageChange={this.handlePageClick}
                            onPageChange={() => { }}
                            containerClassName={"pagination react-paginate"}
                            subContainerClassName={"pages pagination react-paginate"}
                            pageLinkClassName={"list-group-item list-group-item-action"}
                            previousLinkClassName={"list-group-item list-group-item-action"}
                            nextLinkClassName={"list-group-item list-group-item-action"}
                            breakLinkClassName={"list-group-item list-group-item-action"}
                            activeClassName={"active"}
                        />
                    </Grid.Row>
                }
            </Page.Content>
        </SiteWrapper >
    )
}
export default DetectorPage;
