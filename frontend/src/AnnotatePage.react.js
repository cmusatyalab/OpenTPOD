import React from 'react';
import { Button, Avatar, Tag, Grid, Page, Icon, Form } from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import { CVATAnnotation } from "./CVATHTML"
import CreatableSelect from 'react-select/creatable';
import $ from 'jquery';

import './engine/base.css'
import './engine/stylesheet.css'

function load_script(src) {
    return new Promise(function (resolve, reject) {
        var script = document.createElement('script');
        script.src = src;
        script.async = false;
        document.body.appendChild(script);
        script.addEventListener('load', function () {
            resolve();
        });
        script.addEventListener('error', function (e) {
            reject(e);
        });
    })
};

var cvat_js_files = [
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
window.callAnnotationUI = (e) => { };


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

class AnnotatePage extends React.Component {
    constructor(props) {
        super(props);
        this.loadExternalJSByIdx = this.loadExternalJSByIdx.bind(this)
        this.renderAnnotationUIWithCVAT = this.renderAnnotationUIWithCVAT.bind(this)
    }

    renderAnnotationUIWithCVAT() {
        // finished loading scripts, init UI using cvat 
        window.callAnnotationUI(this.props.match.params.vid);
        customizeCVATUI()
    }

    loadExternalJSByIdx(idx, load_func) {
        load_cvat_js[idx].then(() => {
            if (idx + 1 < load_cvat_js.length) {
                load_func(idx + 1, load_func)
            } else if (idx + 1 == load_cvat_js.length) {
                this.renderAnnotationUIWithCVAT()
            }
        }).catch(function (e) {
            console.error('error loading cvat js')
            console.error(e)
        })
    }

    componentDidMount() {
        this.loadExternalJSByIdx(0, this.loadExternalJSByIdx);
        window.callAnnotationUI(45);
    }

    createNewLabel() {
        // create new labels
    }

    render() {
        return <SiteWrapper>
            <Page.Content>
                {/* <LabelPanel /> */}
                <hr />
                <CVATAnnotation />
            </Page.Content >
        </SiteWrapper >
    }
}

export default AnnotatePage;