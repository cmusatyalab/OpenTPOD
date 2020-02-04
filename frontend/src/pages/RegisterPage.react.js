import * as React from "react";
import * as EmailValidator from "email-validator";
import * as passwordValidator from "password-validator";
import { Formik } from "formik";
import { RegisterPage as TablerRegisterPage } from "tabler-react";
import { withRouter } from "react-router";
import { fetchJSON, withFormikStatus } from "../util";
import { endpoints } from "../const";
import { TablerLoginPage } from "./TablerLoginPage.react";

const pageStrings = {
    title: "Create a New Account",
    buttonText: "Register",
    emailLabel: "Email Address",
    emailPlaceholder: "Enter email",
    passwordLabel: "Password",
    passwordPlaceholder: "Password"
};

class RegisterPage extends React.Component {
    constructor(props) {
        super(props);
        this.schema = new passwordValidator();
        // Add properties to it
        this.schema
            .is()
            .min(6) // Minimum length 6
            .is()
            .max(24) // Maximum length 24
            .has()
            .not()
            .spaces(); // Should not have spaces
    }

    render() {
        return (
            <Formik
                initialValues={{
                    email: "",
                    password: ""
                }}
                validate={values => {
                    let errors = {};
                    // check email
                    if (!values.email) {
                        errors.email = "Required";
                    } else if (!EmailValidator.validate(values.email)) {
                        errors.email = "Invalid email address";
                    }

                    // check password
                    if (!values.password) {
                        errors.password = "Required";
                    } else if (!this.schema.validate(values.password)) {
                        errors.password =
                            "Password should have 6-24 non-space characters.";
                    }
                    return errors;
                }}
                onSubmit={(values, actions) => {
                    const data = {
                        email: values.email,
                        username: values.email,
                        // choose not to verify the password
                        password1: values.password,
                        password2: values.password
                    };
                    fetchJSON(endpoints.registeration, "POST", data)
                        .then(() => {
                            actions.setStatus(
                                "Registration Succeed! Redirecting to your home page..."
                            );
                            setTimeout(
                                () =>
                                    this.props.history.push(endpoints.uiVideo),
                                2000
                            );
                        })
                        .catch(e => {
                            console.error(e);
                            e.text().then(text => {
                                actions.setStatus(
                                    "Registration Failed: " + text
                                );
                            });
                        });
                }}
                render={({
                    values,
                    errors,
                    status,
                    touched,
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
                            strings={pageStrings}
                            imageURL={endpoints.logo}
                        />
                    );
                    return withFormikStatus(el, status);
                }}
            />
        );
    }
}

export default withRouter(RegisterPage);
