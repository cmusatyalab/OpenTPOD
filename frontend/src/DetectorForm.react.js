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

const DetectorNewForm = props => {
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
    const [activeDnnType, setActiveDnnType] = useState(null);
    const [trainingConfig, setTrainingConfig] = useState(null);
    const [trainingConfigLoading, setTrainingConfigLoading] = useState(false);
    const [taskSelectOptions, onTaskSelectOptionsChange] = useState(null);

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

    const renderTrainingConfig = trainingConfig => {
        let requireds = trainingConfig.required;
        let optionals = trainingConfig.optional;

        let requiredFields = requireds.map((item, index) => (
            <FormTextInput
                key={index}
                name={item}
                type="text"
                label={item}
                // onChange={onChange}
                // onBlur={onBlur}
                // value={values && values.password}
                // error={errors && errors.password}
            />
        ));

        let optionalFields = Object.entries((item, index) => (
            <FormTextInput
                key={index}
                name={item[0]}
                type="text"
                label={item[0]}
                placeholder={item[1]}
                // onChange={onChange}
                // onBlur={onBlur}
                // value={values && values.password}
                // error={errors && errors.password}
            />
        ));

        if (requireds.length + Object.keys(optionals).length > 0) {
            return (
                <Form.FieldSet>
                    {requiredFields}
                    {optionalFields}
                </Form.FieldSet>
            );
        }
    };

    useEffect(() => {
        fetchSupportedDnnTypes();
    }, []);

    return dnnTypes == null ? (
        <Dimmer active loader />
    ) : (
        <FormCard
            buttonText={strings.buttonText || defaultStrings.buttonText}
            title={strings.title || defaultStrings.title}
            onSubmit={onSubmit}
            action={action}
            method={method}
        >
            <FormTextInput
                name="name"
                label={strings.nameLabel || defaultStrings.nameLabel}
                placeholder={
                    strings.namePlaceholder || defaultStrings.namePlaceholder
                }
                onChange={onChange}
                onBlur={onBlur}
                value={values && values.name}
                error={errors && errors.name}
            />
            <Form.Group label={"Training Videos"}>
                <AsyncPaginate
                    styles={reactSelectTablerStyles}
                    debounceTimeout={300}
                    value={taskSelectOptions}
                    initialOptions={[]}
                    loadOptions={loadAndSearchTasks}
                    onChange={onTaskSelectOptionsChange}
                    isMulti
                    closeMenuOnSelect={false}
                    additional={{
                        page: 1
                    }}
                />
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
                    }}
                />
            </Form.Group>
            {trainingConfig && renderTrainingConfig(trainingConfig)}
            <FormTextInput
                name="Training Configurations"
                label={strings.emailLabel || defaultStrings.emailLabel}
                placeholder={
                    strings.emailPlaceholder || defaultStrings.emailPlaceholder
                }
                onChange={onChange}
                onBlur={onBlur}
                value={values && values.email}
                error={errors && errors.email}
            />
            {/* <FormCheckboxInput
                onChange={onChange}
                onBlur={onBlur}
                value={values && values.terms}
                name="terms"
                label={strings.termsLabel || defaultStrings.termsLabel}
            /> */}
        </FormCard>
    );
};

export { DetectorNewForm };
