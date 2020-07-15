import * as React from "react";
import {
    BrowserRouter as Router,
    Route,
    Switch,
    Redirect
} from "react-router-dom";
// standard pages
import {
    ForgotPasswordPage,
    LoginPage,
    RegisterPage,
    Error400,
    Error401,
    Error403,
    Error404,
    Error500,
    Error503
} from "./pages";
import VideoPage from "./VideoPage.react";
import DataPage from "./LoadDataPage.react";
// import ModelPage from "./LoadModelPage.react";
import { LabelManagementPage } from "./Label.react";
import AnnotatePage from "./AnnotatePage.react";
import {
    DetectorPage,
    DetectorDetailPage,
    DetectorNewPage
} from "./DetectorPage.react";
import { LoadModelPage,ModelNewPage } from "./LoadModelPage.react"
import { endpoints } from "./const";
import "tabler-react/dist/Tabler.css";
import { uiAuth } from "./util.js";

const AuthRequiredRoute = ({ component: Component, ...rest }) => (
    <Route
        {...rest}
        render={props =>
            uiAuth.isAuthenticated() === true ? (
                <Component {...props} />
            ) : (
                <Redirect to={endpoints.uiHome} />
            )
        }
    />
);

function App(props) {
    return (
        <Router>
            <Switch>
                <Route exact path={endpoints.uiHome} component={LoginPage} />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiVideo}
                    component={VideoPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiLoadData}
                    component={DataPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiLabel}
                    component={LabelManagementPage}
                />
                <AuthRequiredRoute
                    exact
                    // path={endpoints.detectormodels}
                    path={endpoints.uiLoadModel}
                    component={LoadModelPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiAnnotate + "/tasks/:tid"}
                    component={AnnotatePage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiDetector}
                    component={DetectorPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiDetector + "/:id"}
                    component={DetectorDetailPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiDetectorNew}
                    component={DetectorNewPage}
                />
                <AuthRequiredRoute
                    exact
                    path={endpoints.uiModelNew}
                    component={ModelNewPage}
                />
                <Route
                    exact
                    path="/forgot-password"
                    component={ForgotPasswordPage}
                />
                <Route exact path={endpoints.uiLogin} component={LoginPage} />
                <Route
                    exact
                    path={endpoints.uiSignup}
                    component={RegisterPage}
                />
                <Route exact path="/400" component={Error400} />
                <Route exact path="/401" component={Error401} />
                <Route exact path="/403" component={Error403} />
                <Route exact path="/404" component={Error404} />
                <Route exact path="/500" component={Error500} />
                <Route exact path="/503" component={Error503} />
                <Route component={Error404} />
            </Switch>
        </Router>
    );
}

export default App;
