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
                <Card.Options>{options}</Card.Options>
            </Card.Header>
            <Card.Body>{body}</Card.Body>
        </Card>
    );
};

// a list of info card wrapped with Grid Col
const InfoCardList = ({
    iterableResourceObjs,
    Title,
    Options,
    Body,
    makeTitle,
    makeOptions,
    makeBody,
    cardColumnWidth = 3,
    ...rest
}) => {
    // Title, Options, Body are React component types
    // makeTitle, makeOptions, makeBody are three functions that takes a
    // resourceObj and produce UI elements
    // Title, Options, Body have precedence over make... functions
    let cards = iterableResourceObjs.map((item, index) => {
        // if (item.name.endsWith(".tfrecord") || item.name.endsWith(".pbtxt")) {
        //     return ""
        // }
        return (
            <Grid.Col auto key={index} sm={cardColumnWidth}>
                <InfoCard
                    title={
                        Title ? (
                            <Title resourceObj={item} {...rest} />
                        ) : (
                            makeTitle(item)
                        )
                    }
                    options={
                        Options ? (
                            <Options resourceObj={item} {...rest} />
                        ) : (
                            makeOptions(item)
                        )
                    }
                    body={
                        Body ? (
                            <Body resourceObj={item} {...rest} />
                        ) : (
                            makeBody(item)
                        )
                    }
                    {...rest}
                />
            </Grid.Col>
        );
    });
    return <>{cards}</>;
};

// a paginated list of info card supporting showing paginated results
const PaginatedInfoCardList = ({
    iterableResourceObjs,
    forcePage,
    onPageChange,
    pageCount,
    Title,
    Options,
    Body,
    makeTitle,
    makeOptions,
    makeBody,
    cardColumnWidth = 6,
    pageNavOffset = 0,
    ...rest
}) => (
    <>
        <Grid.Row alignItems="top">
            <Grid.Col offset={pageNavOffset}>
                <ReactPaginate
                    previousLabel={"<"}
                    nextLabel={">"}
                    breakLabel={"..."}
                    pageCount={pageCount}
                    marginPagesDisplayed={1}
                    pageRangeDisplayed={5}
                    forcePage={forcePage}
                    onPageChange={onPageChange}
                    containerClassName={"pagination react-paginate"}
                    pageLinkClassName={"btn btn-md btn-secondary"}
                    previousLinkClassName={"btn btn-md btn-secondary"}
                    nextLinkClassName={"btn btn-md btn-secondary"}
                    breakLinkClassName={"btn btn-md btn-secondary"}
                    activeClassName={"react-paginate-active"}
                />
            </Grid.Col>
        </Grid.Row>
        <Grid.Row>
            <InfoCardList
                iterableResourceObjs={iterableResourceObjs}
                Title={Title}
                Options={Options}
                Body={Body}
                makeTitle={makeTitle}
                makeOptions={makeOptions}
                makeBody={makeBody}
                cardColumnWidth={cardColumnWidth}
                {...rest}
            />
        </Grid.Row>
    </>
);

export { InfoCard, InfoCardList, PaginatedInfoCardList };
