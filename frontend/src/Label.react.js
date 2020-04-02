import React from "react";
import {
    Button,
    Tag,
    Container,
    Grid,
    Page,
    Card,
    List,
    Form,
    FormTextInput
} from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import CreatableSelect from "react-select/creatable";
import { Formik } from "formik";

function LabelCard({ labels, onRemove }) {
    const tags = labels.map((curLabel, index) => {
        return (
            <Tag
                remove
                rounded
                color="grey-dark"
                addOnIcon="tag"
                key={index}
                onRemoveClick={onRemove}
            >
                {curLabel.name}
            </Tag>
        );
    });

    let tagList = <Tag.List>{tags}</Tag.List>;

    if (tags.length === 0) {
        tagList = <p>No Labels</p>;
    }

    return (
        <Card>
            <Card.Header>
                <Card.Title>Objects in This Video</Card.Title>
            </Card.Header>
            <Card.Body>{tagList}</Card.Body>
        </Card>
    );
}

function NewLabelCard({ onCancel, onSave }) {
    return (
        <Card>
            <Card.Header>
                <Card.Title>New Object of Interest</Card.Title>
            </Card.Header>
            <Card.Body>
                <Formik
                    validate={values => {
                        let errors = {};
                        if (/^[A-Z0-9a-z]+$/i.test(values.labelValue)) {
                        } else {
                            errors.labelValue =
                                "Invalid Label Name. Aphanumeric Characters [A-Za-z0-9] only.";
                        }
                        return errors;
                    }}
                    onSubmit={(values, { setSubmitting }) => {
                        setSubmitting(true);
                        onSave(values);
                    }}
                    render={({
                        values,
                        errors,
                        handleChange,
                        handleSubmit
                    }) => (
                        <Form onSubmit={handleSubmit}>
                            <Form.Group>
                                <Grid.Row className="align-items-center">
                                    <Grid.Col sm={2}>Text:</Grid.Col>
                                    <Grid.Col sm={10}>
                                        <FormTextInput
                                            name="labelValue"
                                            value={values && values.labelValue}
                                            error={errors && errors.labelValue}
                                            onSubmit={handleSubmit}
                                            onChange={handleChange}
                                        />
                                    </Grid.Col>
                                </Grid.Row>
                            </Form.Group>
                            <Form.Group>
                                <Button.List className="mt-4" align="right">
                                    <Button
                                        color="secondary"
                                        type="button"
                                        onClick={onCancel}
                                    >
                                        Cancel
                                    </Button>
                                    <Button color="primary" type="submit">
                                        Save
                                    </Button>
                                </Button.List>
                            </Form.Group>
                        </Form>
                    )}
                />
            </Card.Body>
        </Card>
    );
}

class LabelManagementPanel extends React.Component {
    state = {
        rightPanel: "labels"
    };

    onNewLabelCardCancel = e => {
        e.preventDefault();
        this.setState({ rightPanel: "labels" });
    };

    onNewLabelCardSave = values => {
        const labelValue = values.labelValue;
        this.props.onAddLabel(labelValue);
        this.setState({
            rightPanel: "labels"
        });
    };

    onLabelTagRemove = e => {
        const label = e.target.parentNode.parentNode.textContent;
        this.props.onDeleteLabel(label);
    };

    render() {
        let rightPanel = null;
        if (this.state.rightPanel === "labels") {
            rightPanel = (
                <LabelCard
                    labels={this.props.labels}
                    onRemove={this.onLabelTagRemove}
                />
            );
        } else if (this.state.rightPanel === "newLabel") {
            rightPanel = (
                <NewLabelCard
                    onCancel={this.onNewLabelCardCancel}
                    onSave={this.onNewLabelCardSave}
                />
            );
        }

        return (
            <Container>
                <div className="my-3 my-md-5">
                    <Grid.Row>
                        <Grid.Col md={3}>
                            <div>
                                <List.Group transparent={true}>
                                    <List.GroupItem
                                        RootComponent="div"
                                        className="d-flex align-items-center"
                                    >
                                        <Button
                                            outline
                                            icon="plus-circle"
                                            color="primary"
                                            onClick={e => {
                                                this.setState({
                                                    rightPanel: "newLabel"
                                                });
                                            }}
                                        >
                                            New Objects of Interest
                                        </Button>
                                    </List.GroupItem>
                                </List.Group>
                            </div>
                        </Grid.Col>
                        <Grid.Col md={9}>{rightPanel}</Grid.Col>
                        {this.state.addNewLabel && (
                            <Grid>
                                <Grid.Row>
                                    <Grid.Col>
                                        <CreatableSelect
                                            isMulti
                                            options={this.state.labels}
                                        />
                                    </Grid.Col>
                                    <Grid.Col>
                                        <Button
                                            RootComponent="button"
                                            color="primary"
                                            onClick={this.addLabels}
                                        >
                                            Add
                                        </Button>
                                    </Grid.Col>
                                </Grid.Row>
                            </Grid>
                        )}
                    </Grid.Row>
                </div>
            </Container>
        );
    }
}

class LabelManagementPage extends React.Component {
    render() {
        return (
            <SiteWrapper>
                <Page.Content title="Label Dashboard">
                    {
                        // used by annotatepage.react.js
                        /* <LabelManagementPanel /> */
                    }
                </Page.Content>
            </SiteWrapper>
        );
    }
}
export { LabelManagementPanel, LabelManagementPage };
