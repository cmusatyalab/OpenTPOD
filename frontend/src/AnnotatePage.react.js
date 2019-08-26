import $ from 'jquery';
import React from 'react';
import { Dimmer, Page, Grid } from "tabler-react";
import { CVATAnnotationHTML } from "./CVATHTML";
import { LabelManagementPanel } from './Label.react';
import SiteWrapper from "./SiteWrapper.react";
import { fetchJSON } from "./util"
import URI from "urijs";
import { endpoints } from "./url";

function get_url_extension(url) {
    return url.split(/\#|\?/)[0].split('.').pop().trim();
}

function load_script(src) {
    let ext = get_url_extension(src)
    return new Promise(function (resolve, reject) {
        let script = null;
        if (ext === 'js') {
            script = document.createElement('script');
            script.src = src;
            script.async = false;
            document.body.appendChild(script);
        } else if (ext === 'css') {
            let head = document.getElementsByTagName('head')[0];
            script = document.createElement('link');
            script.rel = 'stylesheet';
            script.type = 'text/css';
            script.href = src;
            script.media = 'all';
            head.appendChild(script);
        } else {
            throw "Unsupported file type to load dynamically (" + src + ")."

        }
        script.addEventListener('load', function () {
            resolve();
        });
        script.addEventListener('error', function (e) {
            reject(e);
        });
    })
};

var cvat_js_files = [
    'static/engine/base.css',
    'static/engine/stylesheet.css',
    'static/engine/js/3rdparty/jquery-3.3.1.js',
    'static/engine/js/3rdparty/jquery.fullscreen.js',
    'static/engine/js/3rdparty/js.cookie.js',
    'static/engine/js/3rdparty/mousetrap.js',
    'static/engine/js/3rdparty/svg.js',
    'static/engine/js/3rdparty/svg.draw.js',
    'static/engine/js/3rdparty/svg.resize.min.js',
    'static/engine/js/3rdparty/svg.draggable.js',
    'static/engine/js/3rdparty/svg.select.js',
    'static/engine/js/3rdparty/defiant.min.js',
    'static/engine/js/base.js',
    'static/engine/js/logger.js',
    'static/engine/js/server.js',
    'static/engine/js/listener.js',
    'static/engine/js/history.js',
    'static/engine/js/userConfig.js',
    'static/engine/js/coordinateTranslator.js',
    'static/engine/js/labelsInfo.js',
    'static/engine/js/annotationParser.js',
    'static/engine/js/attributeAnnotationMode.js',
    'static/engine/js/shapeFilter.js',
    'static/engine/js/shapeSplitter.js',
    'static/engine/js/polyshapeEditor.js',
    'static/engine/js/shapes.js',
    'static/engine/js/shapeCollection.js',
    'static/engine/js/player.js',
    'static/engine/js/shapeMerger.js',
    'static/engine/js/shapeBuffer.js',
    'static/engine/js/shapeCreator.js',
    'static/engine/js/shapeGrouper.js',
    'static/engine/js/annotationSaver.js',
    'static/engine/js/annotationUI.js',
]

var load_cvat_js = cvat_js_files.map(load_script);

// this is a dummy definition so that
// compiler doesn't complain about function not found
// this function will be overriden by callAnnotationUI
// in the engine/js/annotaionUI.js
window.callAnnotationUI = () => { };


function customizeCVATUI() {
    // remove unused menu options
    const ids = [
        'undoButton',
        'lastUndoText',
        'lastRedoText',
        'redoButton',
        'resetFilterButton',
        'filterInputString',
        'resetFilterButton',
        'filterLabel',
        'filterSubmitList',
        'filterSelect',
        'fillOptionTable',
        'mergeTracksButton',
        'groupShapesButton',
        'shapeTypeSelector',
        'polyShapeSizeWrapper',
    ];
    ids.map((item, index) => {
        const jitem = $('#' + item)
        jitem.css({
            'margin-left': '0px',
            'margin-right': '0px',
            'width': '0px',
            'display': 'none',
        })
        jitem.hide()
    });

    //rename buttons to make their meaning clear
    $('#menuButton').text('Actions')
    $('#createShapeButton').text('Annotate')
}

function clearCVATUI() {
    // CVAT build annotation assumes a clean start for HTML elements
    // however, react won't render them. leaving side-effects of preivous renders.
    // this functions clear the CVAT UI for re-build
    // TODO(junjuew): doesn't seem to be working. the options still have duplicates
    // need to move this to shapeCreator
    $("#shapeLabelSelector").empty();
}

class CVATAnnotation extends React.Component {
    renderAnnotationUIWithCVAT = () => {
        // build CVAT annotation UI using cvat js
        window.callAnnotationUI(this.props.jid);
        // customizeCVATUI();
    }

    loadExternalJSByIdx = (idx, load_func) => {
        load_cvat_js[idx].then(() => {
            if (idx + 1 < load_cvat_js.length) {
                load_func(idx + 1, load_func);
            } else if (idx + 1 == load_cvat_js.length) {
                this.renderAnnotationUIWithCVAT();
            }
        }).catch(function (e) {
            console.error('error loading cvat js');
            console.error(e);
        })
    }

    componentDidMount = () => {
        this.loadExternalJSByIdx(0, this.loadExternalJSByIdx);
    }

    render = () => {
        this.renderAnnotationUIWithCVAT();
        return <CVATAnnotationHTML />
    }
}

class AnnotatePage extends React.Component {
    state = {
        labels: [],
        loading: true
    };
    taskInfo = null;

    getLabels = () => {
        fetchJSON(URI.joinPaths(endpoints.tasks,
            this.props.match.params.tid), "GET").then(
                resp => {
                    this.taskInfo = resp;
                    this.setState({
                        labels: resp.labels,
                        loading: false
                    });
                });
    }

    addLabel = (label) => {
        const curLabels = this.state.labels.slice(0);
        curLabels.push({
            "name": label
        })
        const req = {
            "name": this.taskInfo.name,
            "labels": curLabels,
            "image_quality": this.taskInfo.image_quality
        }
        fetchJSON(URI.joinPaths(endpoints.tasks, this.props.match.params.tid),
            "PATCH", req).then(() => {
                this.getLabels();
            })
    }

    deleteLabel = (label) => {
        // TODO (junjuew): CVAT doesn't seem to have support for removing label yet.
        const curLabels = this.state.labels.filter(
            (value) => {
                return value.name !== label;
            }
        );
        console.log(curLabels);
        const req = {
            "name": this.taskInfo.name,
            "labels": curLabels,
            "image_quality": this.taskInfo.image_quality
        }
        fetchJSON(URI.joinPaths(endpoints.tasks, this.props.match.params.tid),
            "PATCH", req).then(() => {
                this.getLabels();
            })
    }

    componentDidMount() {
        this.getLabels();
    }

    render() {
        return (
            <SiteWrapper>
                <Page.Content title="What do you want to label?" style={{ height: "100%" }}>
                    <Grid.Row>
                        <section className="container">
                            {
                                (this.state.loading) ?
                                    <Dimmer active loader /> : <>
                                        <LabelManagementPanel
                                            taskID={this.props.match.params.tid}
                                            labels={this.state.labels}
                                            onAddLabel={this.addLabel}
                                            onDeleteLabel={this.deleteLabel}
                                        />
                                        {
                                            this.state.labels.length !== 0 &&
                                            <CVATAnnotation
                                                jid={this.props.match.params.jid}
                                                labels={this.state.labels}
                                            />
                                        }
                                    </>
                            }
                        </section>
                    </Grid.Row>
                </Page.Content>
            </SiteWrapper>
        )
    }
}

export default AnnotatePage;