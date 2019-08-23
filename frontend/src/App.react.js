import * as React from "react";
import { HashRouter as Router, Redirect, Route, Switch } from "react-router-dom";
import {
  ForgotPasswordPage,
  LoginPage,
  RegisterPage,
  Error400,
  Error401,
  Error403,
  Error404,
  Error500,
  Error503,
} from "./pages";

import VideoPage from "./VideoPage.react"
import { LabelManagementPage } from "./Label.react"
import AnnotatePage from "./AnnotatePage.react";
import TrainPage from "./TrainPage.react";

import "tabler-react/dist/Tabler.css";

type Props = {||};

function App(props: Props): React.Node {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={LoginPage} />
        <Route exact path="/video" component={VideoPage} />
        <Route exact path="/label" component={LabelManagementPage} />
        <Route exact path="/annotate/:vid" component={AnnotatePage} />
        <Route exact path="/train" component={TrainPage} />
        <Route exact path="/forgot-password" component={ForgotPasswordPage} />
        <Route exact path="/login" component={LoginPage} />
        <Route exact path="/register" component={RegisterPage} />
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
