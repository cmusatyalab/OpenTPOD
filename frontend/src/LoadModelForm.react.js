import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import Select from "react-select";
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";
import AsyncPaginate from "react-select-async-paginate";
import { Formik } from "formik";
import URI from "urijs";
import { Dimmer, Form, FormTextInput, FormCard } from "tabler-react";
// import { endpoints, reactSelectTablerStyles } from "./const";
import { fetchJSON } from "./util";
import defaultStrings from "./DetectorPage.strings";
import "./App.css";
import { endpoints, PAGE_SIZE, session_storage_key } from "./const";
import { FilePond, registerPlugin } from "react-filepond";

const NewDetectorForm = ({ strings = {} }) => {
    let history = useHistory();
    // const [model, setmodel] = useState(null);
    // form values. Set as a state variable as we're updating it
    // both from default values of the backend and user input
    // const [formInitialValues, setFormInitialValues] = useState({
    //     name: "",
    //     model: null
    // });
    // const [videos, setVideos] = useState(null);
    const [files, setFiles] = useState([]);
    // const [curPage, setCurPage] = useState(null);

    const createTask = ({
        // data,
        // onTaskCreated,
        userId,
        fieldName,
        file,
        progress,
        load,
        error,
        abort
    }) => {
        // fetchJSON(endpoints.detectormodels, "POST", data)
        //     .then(resp => {
                // fieldName is the name of the input field
                // file is the actual file object to send
                console.log(fieldName)
                const formData = new FormData();
                formData.append("file", file);
                const request = new XMLHttpRequest();
                
                request.open(
                    "POST",
                    endpoints.detectormodels
                    // URI.joinPaths(endpoints.detectormodels, resp.id.toString())
                );
                
                // const batchOfFiles = new FormData();
                // batchOfFiles.append("client_files[0]", file);
                // const request = new XMLHttpRequest();
                // request.open(
                //     "POST",
                //     URI.joinPaths(endpoints.mediaData, resp.id.toString(), "data")
                // );
                // // Should call the progress method to update the progress to 100% before calling load
                // // Setting computable to false switches the loading indicator to infinite mode
                request.upload.onprogress = e => {
                    progress(e.lengthComputable, e.loaded, e.total);
                };
                // Should call the load method when done and pass the returned server file id
                // this server file id is then used later on when reverting or restoring a file
                // so your server knows which file to return without exposing
                // that info to the client
                // this is called when the request transaction is finished
                request.onload = function() {
                    if (request.status >= 200 && request.status < 300) {
                        // the load method accepts either a string (id) or an object
                        load(request.responseText);
                        // onTaskCreated();
                    } else {
                        // Can call the error method if something is wrong, should exit after
                        error("File Upload Failed");
                        abort();
                    }
                };
                // request.send(batchOfFiles);
                formData.append("owner", userId)
                request.send(formData);
                // Should expose an abort method so the request can be cancelled
                return {
                    abort: () => {
                        // This function is entered if the user has tapped the cancel button
                        request.abort();
                        // Let FilePond know the request has been cancelled
                        abort();
                    }
                };
            // })
            // .catch(e => {
            //     console.error(e);
            //     error(e);
            //     abort();
            // });
    };
    

    return (
        // <Formik
        //     render={({
        //         values,
        //         errors,
        //         handleChange,
        //         handleSubmit,
        //         isSubmitting
        //     }) =>
                // isSubmitting ? (
                //     <Dimmer active loader />
                // ) : 
                // (
                    <FormCard
                    >
                        <FilePond
                            labelIdle="Drag & Drop Model File or Click to Browse. (in .zip)"
                            files={files}
                            allowMultiple={true}
                            server={{
                                process: (
                                    fieldName,
                                    file,
                                    metadata,
                                    load,
                                    error,
                                    progress,
                                    abort
                                ) => {
                                    // create CVAT task first
                                    let userId = sessionStorage.getItem(
                                        session_storage_key.userId
                                    );
                                    createTask({
                                        userId,
                                        fieldName,
                                        file,
                                        progress,
                                        load,
                                        error,
                                        abort
                                    });
                                },

                                fetch: null,
                                revert: null,
                                load: null
                            }}
                            allowRevert={false}
                            onupdatefiles={fileItems => {
                                // Set currently active file objects
                                setFiles(
                                    fileItems.map(fileItem => fileItem.file)
                                );
                            }}
                            onprocessfiles={() => {
                                setFiles([]);
                            }}
                        />
                    </FormCard>
        //         )
        //     }
        // />
    );
};

export { NewDetectorForm };
