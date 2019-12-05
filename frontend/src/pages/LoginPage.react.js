import * as React from "react";
import { Formik } from "formik";
import { LoginPage as TablerLoginPage, Alert } from "tabler-react";
import { fetchJSON, withFormikStatus } from "../util";
import { withRouter } from "react-router";
import { endpoints } from "../const";

class LoginPage extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <Formik
                    initialValues={{
                        email: "",
                        password: ""
                    }}
                    validate={values => {
                        let errors = {};
                        if (!values.email) {
                            errors.email = "Required";
                        }
                        return errors;
                    }}
                    onSubmit={(values, actions) => {
                        let email = "";
                        let username = "";
                        if (
                            /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(
                                values.email
                            )
                        ) {
                            email = values.email;
                        } else {
                            username = values.email;
                        }
                        const data = {
                            username: username,
                            email: email,
                            password: values.password
                        };
                        fetchJSON(endpoints.login, "POST", data)
                            .then(resp => {
                                actions.setStatus("Login success: ");
                                this.props.history.push(endpoints.uiVideo);
                            })
                            .catch(e => {
                                console.error(e);
                                actions.setStatus("Login Failed: " + e);
                            });
                    }}
                    render={({
                        values,
                        errors,
                        touched,
                        status,
                        handleChange,
                        handleBlur,
                        handleSubmit,
                        isSubmitting
                    }) => {
                        let el = (
                            <TablerLoginPage
                                onSubmit={handleSubmit}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                values={values}
                                errors={errors}
                                touched={touched}
                            />
                        );
                        return withFormikStatus(el, status);
                    }}
                />
                <div className="text-center text-muted">
                    Don't have account yet? <a href="#/register">Sign up</a>
                </div>
            </div>
        );
    }
}

export default withRouter(LoginPage);
