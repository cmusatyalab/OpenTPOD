// @flow

import * as React from "react";
import * as EmailValidator from "email-validator";
import * as passwordValidator from "password-validator";
import { Formik } from "formik";
import { RegisterPage as TablerRegisterPage, Alert } from "tabler-react";
import { withRouter } from 'react-router';

import { fetchJSON, withFormikStatus } from '../util';


class RegisterPage extends React.Component {
    constructor(props) {
        super(props)
        this.schema = new passwordValidator();
        // Add properties to it
        this.schema
            .is().min(6)                                    // Minimum length 8
            .is().max(24)                                  // Maximum length 24
            .has().not().spaces()                           // Should not have spaces
    }

    render() {
        return <Formik
            initialValues={{
                name: "",
                email: "",
                password: "",
            }}
            validate={values => {
                let errors = {};
                // check email
                if (!values.email) {
                    errors.email = "Required";
                } else if (
                    !EmailValidator.validate(values.email)
                ) {
                    errors.email = "Invalid email address";
                }

                // check password
                if (!values.password) {
                    errors.password = "Required";
                } else if (
                    !this.schema.validate(values.password)
                ) {
                    errors.password = "Password should have 6-24 non-space characters.";
                }
                return errors;
            }}
            onSubmit={(
                values,
                actions
            ) => {
                const data = {
                    'email': values.email,
                    'password': values.password,
                    'username': values.name
                }
                fetchJSON('/api/users', 'POST', data).then(
                    resp => {
                        actions.setStatus('Registration Succeed! Redirecting to login page...');
                        setTimeout(
                            () => this.props.history.push('/login'),
                            2000
                        )
                    }
                ).catch(
                    e => {
                        console.error(e)
                        actions.setStatus('Registration Failed: ' + e);
                    });
            }
            }
            render={({
                values,
                errors,
                status,
                touched,
                handleChange,
                handleBlur,
                handleSubmit,
                isSubmitting
            }) => {
                let el = <TablerRegisterPage
                    onSubmit={handleSubmit}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    values={values}
                    errors={errors}
                    touched={touched}
                />;
                return withFormikStatus(el, status)
            }
            }
        />
    }
}

export default withRouter(RegisterPage);
