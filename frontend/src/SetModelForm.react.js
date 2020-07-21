import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import Select from "react-select";
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";
import AsyncPaginate from "react-select-async-paginate";
import { Formik } from "formik";
import URI from "urijs";
import { Dimmer, Form, FormTextInput, FormCard } from "tabler-react";
// import { endpoints, reactSelectTablerStyles } from "./const";
import { lineWrap, fetchJSON } from "./util";
import defaultStrings from "./DetectorPage.strings";
import "./App.css";
import { endpoints, PAGE_SIZE, session_storage_key } from "./const";

const SetModelForm = ({ strings = {} }) => {
    let history = useHistory();
    // const [model, setmodel] = useState(null);
    const [currentModel, setCurrentModel] = useState(null);
    // form values. Set as a state variable as we're updating it
    // both from default values of the backend and user input
    const [formInitialValues, setFormInitialValues] = useState({
        name: ""
    });

    const fetchCurrentModel = () => {
        fetchJSON(endpoints.currentmodel, "GET").then(resp => {
            let model = JSON.parse(resp);
            console.log(model)
            // let typeOptions = types.map(item => ({
            //     value: item[0],
            //     label: item[1]
            // }));
            // setAvailableDnnTypes(typeOptions);
        });
    };

    useEffect(() => {
        fetchCurrentModel();
    }, []);

    return (
        <Formik
            enableReinitialize={true}
            initialValues={formInitialValues}
            validate={values => {
                let errors = {};
                if (!values.name) {
                    errors.name = "Required";
                }
                // values.model = files[0]
                console("validate values: " + JSON.stringify(values));
                return errors;
            }}
            onSubmit={(
                values,
                { setSubmitting /* setErrors, setValues and other goodies */ }
            ) => {
                setSubmitting(true);
                let userId = sessionStorage.getItem(
                    session_storage_key.userId
                );
                console.log(userId)
                let data = {
                    path: values.name,
                    owner: userId
                };
                console.log(data);
                
                fetchJSON(endpoints.setmodels, "POST", data).then(resp => {
                    // history.push(endpoints.uiLoadModel);
                    history.push(endpoints.uiDetector);
                    history.push(endpoints.uiLoadModel);
                });
            }}
            render={({
                values,
                errors,
                handleChange,
                handleSubmit,
                isSubmitting
            }) =>
                isSubmitting ? (
                    <Dimmer active loader />
                ) : (
                    <FormCard
                        buttonText={
                            strings.setmodelbutton || defaultStrings.setmodelbutton
                        }
                        // title={strings.setmodeltitle || defaultStrings.setmodeltitle}
                        onSubmit={handleSubmit}
                    >
                        <FormTextInput
                            name="name"
                            label={
                                strings.setModelLabel || defaultStrings.setModelLabel
                            }
                            placeholder={
                                strings.setModelPlaceholer ||
                                defaultStrings.setModelPlaceholer
                            }
                            value={values && values.name}
                            error={errors && errors.name}
                            onSubmit={handleSubmit}
                            onChange={handleChange}
                        />
                    </FormCard>
                )
            }
        />
    );
};

export { SetModelForm };