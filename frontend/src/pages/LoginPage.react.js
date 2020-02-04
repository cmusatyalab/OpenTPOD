import * as React from "react";
import { Formik } from "formik";
import { uiAuth, withFormikStatus, withTouchedErrors } from "../util";
import { withRouter } from "react-router";
import { endpoints } from "../const";
import { TablerLoginPage } from "./TablerLoginPage.react";

class LoginPage extends React.Component {
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
                        uiAuth
                            .login(data)
                            .then(() => {
                                actions.setStatus("Login success: ");
                                this.props.history.push(endpoints.uiVideo);
                            })
                            .catch(e => {
                                console.error(e);
                                e.text().then(text => {
                                    actions.setStatus("Login Failed: " + text);
                                });
                            });
                    }}
                    render={({
                        values,
                        errors,
                        touched,
                        status,
                        handleChange,
                        handleBlur,
                        handleSubmit
                    }) => {
                        let el = (
                            <TablerLoginPage
                                onSubmit={handleSubmit}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                values={values}
                                errors={errors}
                                touched={touched}
                                imageURL={endpoints.logo}
                            />
                        );
                        return withFormikStatus(el, status);
                    }}
                />
                <div className="text-center text-muted">
                    Don't have account yet?{" "}
                    <a href={endpoints.uiSignup}>Sign up</a>
                </div>
            </div>
        );
    }
}

export default withRouter(LoginPage);
