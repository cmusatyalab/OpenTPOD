import React, { useState, useEffect } from "react";
import { useHistory, useParams } from "react-router-dom";
import Select from "react-select";
import AsyncPaginate from "react-select-async-paginate";
import { Formik } from "formik";
import URI from "urijs";
import {
    Button,
    Card,
    Dimmer,
    Grid,
    Page,
    List,
    Form,
    FormTextInput,
    FormCard
} from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints } from "./url";
import { fetchJSON, lineWrap, downloadByPoll as checkDownload } from "./util";
import defaultStrings from "./DetectorPage.strings";
import "./App.css";

const fetchTasks = async page => {
    let url = new URI(endpoints.tasks);
    url.addSearch("page", page);
    return await fetchJSON(url.toString(), "GET");
};

const filterTasksByName = async searchString => {
    let url = new URI(endpoints.tasks);
    url.addSearch("name", searchString);
    return await fetchJSON(url.toString(), "GET");
};

const loadAndSearchTasks = async (search, options, { page }) => {
    let filteredOptions;
    let hasMore;
    let curTasks;
    let curOptions;
    let nextPage;
    if (!search) {
        curTasks = await fetchTasks(page);
        curOptions = curTasks.results.map(task => {
            return {
                value: task.id,
                label: `${task.id} + ${task.name}`
            };
        });
        // backend's returned count is the total # of entries
        hasMore = curTasks.count > options.length + curOptions.length;
        nextPage = page + 1;
    } else {
        curTasks = await filterTasksByName(search.toLowerCase());
        curOptions = curTasks.results.map(task => {
            return {
                value: task.id,
                label: `${task.id} + ${task.name}`
            };
        });
        hasMore = false;
        nextPage = page;
    }
    filteredOptions = curOptions;
    return {
        options: filteredOptions,
        hasMore: hasMore,
        additional: {
            page: nextPage
        }
    };
};

const reactSelectTablerStyles = {
    control: (provided, state) => ({
        ...provided,
        border: "1px solid rgba(0, 40, 100, 0.12)",
        borderRadius: "3px"
    }),
    placeholder: (provided, state) => ({
        ...provided,
        opacity: "0.6"
    })
};

const TrainingConfig = ({ trainingConfig, values, errors, ...rest }) => {
    let requireds = trainingConfig.required;
    let optionals = trainingConfig.optional;

    let requiredFields = requireds.map((item, index) => {
        values.required[item] = "";
        return (
            <FormTextInput
                isRequired
                key={index}
                name={item}
                type="text"
                label={item}
                value={values && values.required[item]}
                error={errors && errors.required[item]}
                {...rest}
            />
        );
    });

    let optionalFields = Object.entries((item, index) => {
        values.optional[item[0]] = "";
        return (
            <FormTextInput
                key={index}
                name={item[0]}
                type="text"
                label={item[0]}
                placeholder={item[1]}
                value={values && values.optional[item[0]]}
                error={errors && errors.optional[item[0]]}
                {...rest}
            />
        );
    });

    if (requireds.length + Object.keys(optionals).length > 0) {
        return (
            <Form.FieldSet>
                {requiredFields}
                {optionalFields}
            </Form.FieldSet>
        );
    }
};

const NewDetectorForm = props => {
    const {
        action,
        method,
        onSubmit,
        onChange,
        onBlur,
        values,
        strings = {},
        errors
    } = props;
    let history = useHistory();
    const [dnnTypes, setDnnTypes] = useState(null);
    const [tasks, onTaskSelectOptionsChange] = useState([]);
    const [activeDnnType, setActiveDnnType] = useState(null);
    const [trainingConfig, setTrainingConfig] = useState(null);
    const [trainingConfigLoading, setTrainingConfigLoading] = useState(false);

    // get supported dnn types
    const fetchSupportedDnnTypes = () => {
        fetchJSON(endpoints.detectorDnnTypes, "GET").then(resp => {
            let types = JSON.parse(resp);
            let typeOptions = types.map(item => ({
                value: item[0],
                label: item[1]
            }));
            setDnnTypes(typeOptions);
        });
    };

    // fetch training configuration of currently selected dnn type
    const fetchTrainingConfig = selectedOption => {
        if (selectedOption != null) {
            let dnnType = selectedOption.value;
            setTrainingConfigLoading(true);
            fetchJSON(
                URI.joinPaths(endpoints.dnnTrainingConfigs, dnnType),
                "GET"
            )
                .then(resp => {
                    let trainingConfigs = JSON.parse(resp);
                    setTrainingConfig(trainingConfigs);
                })
                .finally(() => {
                    setTrainingConfigLoading(false);
                });
        }
    };

    useEffect(() => {
        fetchSupportedDnnTypes();
    }, []);

    return dnnTypes == null ? (
        <Dimmer active loader />
    ) : (
        <Formik
            initialValues={{
                name: "",
                trainingConfig: {
                    required: {},
                    optional: {}
                }
            }}
            validate={values => {
                let errors = {};
                let errorTrainingConfig = {};
                if (!values.name) {
                    errors.name = "Required";
                }
                if (tasks.length == 0) {
                    errors.tasks = "Required";
                }
                if (!activeDnnType) {
                    errors.activeDnnType = "Required";
                }
                if (trainingConfig && trainingConfig.required) {
                    trainingConfig.required.map(item => {
                        if (
                            !values.trainingConfig.required.hasOwnProperty(
                                item
                            ) ||
                            !values.trainingConfig.required[item]
                        )
                            errorTrainingConfig[item] = "Required";
                    });
                }
                if (Object.keys(errorTrainingConfig).length > 0) {
                    errors.trainingConfig = { required: errorTrainingConfig };
                }
                return errors;
            }}
            onSubmit={(
                values,
                { setSubmitting, setErrors /* setValues and other goodies */ }
            ) => {
                console.log(values);
                console.log(activeDnnType);
                console.log(tasks);
            }}
            render={({
                values,
                errors,
                handleChange,
                handleSubmit,
                validateForm,
                isSubmitting
            }) => (
                <FormCard
                    buttonText={strings.buttonText || defaultStrings.buttonText}
                    title={strings.title || defaultStrings.title}
                    onSubmit={handleSubmit}
                >
                    <FormTextInput
                        name="name"
                        label={strings.nameLabel || defaultStrings.nameLabel}
                        placeholder={
                            strings.namePlaceholder ||
                            defaultStrings.namePlaceholder
                        }
                        value={values && values.name}
                        error={errors && errors.name}
                        onSubmit={handleSubmit}
                        onChange={handleChange}
                    />
                    <Form.Group label={"Training Videos"}>
                        <AsyncPaginate
                            styles={reactSelectTablerStyles}
                            debounceTimeout={300}
                            value={tasks}
                            initialOptions={[]}
                            loadOptions={loadAndSearchTasks}
                            isMulti
                            closeMenuOnSelect={false}
                            additional={{
                                page: 1
                            }}
                            onChange={(...all) => {
                                onTaskSelectOptionsChange(...all);
                                validateForm();
                            }}
                            onSubmit={handleSubmit}
                        />
                        {errors && errors.tasks && (
                            <span className="tabler-invalid-feedback">
                                {errors.tasks}
                            </span>
                        )}
                    </Form.Group>
                    <Form.Group label={"Detector Types"}>
                        <Select
                            name="Dnn Types"
                            styles={reactSelectTablerStyles}
                            options={dnnTypes}
                            value={activeDnnType}
                            isLoading={trainingConfigLoading}
                            isClearable={true}
                            isSearchable={true}
                            onChange={selectedOption => {
                                setActiveDnnType(selectedOption);
                                setTrainingConfig(null);
                                fetchTrainingConfig(selectedOption);
                                validateForm();
                            }}
                            onSubmit={handleSubmit}
                        />
                        {errors && errors.activeDnnType && (
                            <span className="tabler-invalid-feedback">
                                {errors.activeDnnType}
                            </span>
                        )}
                    </Form.Group>
                    {trainingConfig && (
                        <Form.FieldSet>
                            {// required items
                            trainingConfig.required.map((item, index) => (
                                <Form.Group label={item} key={index}>
                                    <Form.Input
                                        isRequired
                                        name={`trainingConfig.required.${item}`}
                                        type="text"
                                        value={
                                            values &&
                                            values.trainingConfig &&
                                            (values.trainingConfig.required[
                                                item
                                            ] ||
                                                "")
                                        }
                                        error={
                                            errors &&
                                            errors.trainingConfig &&
                                            errors.trainingConfig.required[item]
                                        }
                                        onChange={handleChange}
                                        onSubmit={handleSubmit}
                                    />
                                </Form.Group>
                            ))}
                            {Object.entries(trainingConfig.optional).map(
                                (item, index) => (
                                    <Form.Group label={item[0]} key={index}>
                                        <Form.Input
                                            name={`trainingConfig.optional.${item}`}
                                            type="text"
                                            placeholder={item[1]}
                                            value={
                                                values &&
                                                values.trainingConfig &&
                                                (values.trainingConfig.optional[
                                                    item
                                                ] ||
                                                    "")
                                            }
                                            error={
                                                errors &&
                                                errors.trainingConfig &&
                                                errors.trainingConfig.optional[
                                                    item
                                                ]
                                            }
                                            onChange={handleChange}
                                            onSubmit={handleSubmit}
                                        />
                                    </Form.Group>
                                )
                            )}
                        </Form.FieldSet>
                    )}
                </FormCard>
                // <TrainingConfig
                //     trainingConfig={trainingConfig}
                //     values={values && values.trainingConfigs}
                //     errors={errors && errors.trainingConfigs}
                //     onChange={handleChange}
                //     onSubmit={handleSubmit}
                // />
            )}
        />
    );
};

export { NewDetectorForm };
