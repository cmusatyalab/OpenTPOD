import * as React from "react";
import { Formik } from "formik";
import { FormCard, FormTextInput, StandaloneFormPage } from "tabler-react";
import { uiAuth, withFormikStatus, withTouchedErrors } from "../util";
import { withRouter } from "react-router";
import { endpoints } from "../const";

// Modifed from Tablers Login Page in order to customize logo
const defaultStrings = {
    title: "Login to your Account",
    buttonText: "Login",
    emailLabel: "Email Address",
    emailPlaceholder: "Enter email",
    passwordLabel: "Password",
    passwordPlaceholder: "Password"
};

/**
 * A login page
 * Can be easily wrapped with form libraries like formik and redux-form
 */
function ModifiedTablerLoginPage(props) {
    const {
        action,
        method,
        onSubmit,
        onChange,
        onBlur,
        values,
        strings = {},
        imageURL,
        errors
    } = props;

    return (
        <StandaloneFormPage imageURL={imageURL}>
            <FormCard
                buttonText={strings.buttonText || defaultStrings.buttonText}
                title={strings.title || defaultStrings.title}
                onSubmit={onSubmit}
                action={action}
                method={method}
            >
                <FormTextInput
                    name="email"
                    label={strings.emailLabel || defaultStrings.emailLabel}
                    placeholder={
                        strings.emailPlaceholder ||
                        defaultStrings.emailPlaceholder
                    }
                    onChange={onChange}
                    onBlur={onBlur}
                    value={values && values.email}
                    error={errors && errors.email}
                />
                <FormTextInput
                    name="password"
                    type="password"
                    label={
                        strings.passwordLabel || defaultStrings.passwordLabel
                    }
                    placeholder={
                        strings.passwordPlaceholder ||
                        defaultStrings.passwordPlaceholder
                    }
                    onChange={onChange}
                    onBlur={onBlur}
                    value={values && values.password}
                    error={errors && errors.password}
                />
            </FormCard>
        </StandaloneFormPage>
    );
}

const TablerLoginPage = withTouchedErrors(["email", "password"])(
    ModifiedTablerLoginPage
);

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
                                imageURL={"/tpod-logo.png"}
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
