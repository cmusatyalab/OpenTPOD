import React from "react";
import ReactPaginate from "react-paginate";
import { Card, Grid } from "tabler-react";
import "./App.css";

// info card to show resource information
const InfoCard = ({ title, options, body }) => {
    return (
        <Card>
            <Card.Header>
                <Card.Title>{title}</Card.Title>
                <Card.Options>
                    {options}
                </Card.Options>
            </Card.Header>
            <Card.Body>
                {body}
            </Card.Body>
        </Card>
    );
};

// a list of info card wrapped with Grid Col
const InfoCardList = ({ iterableResourceObjs, makeTitle, makeOptions, makeBody, cardColumnWidth = 3, ...rest }) => {
    // makeTitle, makeOptions, makeBody are three functions that
    // takes a resourceObj and produce UI elements
    let cards = iterableResourceObjs.map((item, index) => {
        return (
            <Grid.Col auto key={index} sm={cardColumnWidth}>
                <InfoCard
                    title={makeTitle(item)}
                    options={makeOptions(item)}
                    body={makeBody(item)}
                    {...rest} />
            </Grid.Col>
        );
    });
    return <>{cards}</>;
};

// a paginated list of info card supporting showing paginated results
const PaginatedInfoCardList = ({
    iterableResourceObjs,
    onPageChange,
    pageCount,
    makeTitle,
    makeOptions,
    makeBody,
    cardColumnWidth = 6,
    pageNavOffset = 10,
    ...rest
}) => <>
        <Grid.Row alignItems="top">
            <Grid.Col offset={pageNavOffset}>
                <ReactPaginate
                    previousLabel={"<"}
                    nextLabel={">"}
                    breakLabel={"..."}
                    pageCount={pageCount}
                    marginPagesDisplayed={1}
                    pageRangeDisplayed={2}
                    onPageChange={onPageChange}
                    containerClassName={
                        "pagination react-paginate"
                    }
                    subContainerClassName={
                        "pages pagination react-paginate"
                    }
                    pageLinkClassName={
                        "list-group-item list-group-item-action"
                    }
                    previousLinkClassName={
                        "list-group-item list-group-item-action"
                    }
                    nextLinkClassName={
                        "list-group-item list-group-item-action"
                    }
                    breakLinkClassName={
                        "list-group-item list-group-item-action"
                    }
                    activeClassName={"active"}
                />
            </Grid.Col>
        </Grid.Row>
        <Grid.Row>
            <InfoCardList
                iterableResourceObjs={iterableResourceObjs}
                makeTitle={makeTitle}
                makeOptions={makeOptions}
                makeBody={makeBody}
                cardColumnWidth={cardColumnWidth}
                {...rest}
            />
        </Grid.Row>
    </>

export { InfoCard, InfoCardList, PaginatedInfoCardList };

