/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const {connect} = require('react-redux');
const {dataContainerSelector, chartSelector} = require('../selectors/disaster');

const {getAnalysisData, getData, setDimIdx, getSFurtherResourceData} = require('../actions/disaster');
const Chart = connect(chartSelector, {setDimIdx})(require('../components/Chart'));
const SummaryChart = connect(chartSelector)(require('../components/SummaryChart'));

const DownloadData = require('../components/DownloadData');
const MoreInfo = require('../components/MoreInfo');
const Overview = connect(({disaster = {}}) => ({riskItems: disaster.overview || [] }) )(require('../components/Overview'));
const {Panel, Tooltip, OverlayTrigger} = require('react-bootstrap');
const Nouislider = require('react-nouislider');
const {show, hide} = require('react-notification-system-redux');
const {chartLabelSelector} = require('../selectors/disaster');
const LabelResource = connect(chartLabelSelector, { show, hide, getData: getSFurtherResourceData })(require('../components/LabelResource'));

const DataContainer = React.createClass({
    propTypes: {
        getData: React.PropTypes.func,
        getAnalysis: React.PropTypes.func,
        setDimIdx: React.PropTypes.func,
        showHazard: React.PropTypes.bool,
        className: React.PropTypes.string,
        hazardTitle: React.PropTypes.string,
        analysisType: React.PropTypes.object,
        riskAnalysisData: React.PropTypes.object,
        dim: React.PropTypes.object,
        hazardType: React.PropTypes.shape({
            mnemonic: React.PropTypes.string,
            description: React.PropTypes.string,
            analysisTypes: React.PropTypes.arrayOf(React.PropTypes.shape({
                name: React.PropTypes.string,
                title: React.PropTypes.string,
                href: React.PropTypes.string
                }))
        })
    },
    getDefaultProps() {
        return {
            showHazard: false,
            getData: () => {},
            getAnalysis: () => {},
            className: "col-sm-7"
        };
    },
    getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    getChartData(data, val) {
        const {dim} = this.props;
        const nameIdx = dim === 0 ? 1 : 0;
        return data.filter((d) => d[nameIdx] === val ).map((v) => {return {"name": v[dim], "value": parseInt(v[2], 10)}; });
    },
    renderAnalysisData() {
        const {dim} = this.props;
        const {hazardSet, data, unitOfMeasure} = this.props.riskAnalysisData;
        const tooltip = (<Tooltip id={"tooltip-back"} className="disaster">{'Back to Analysis Table'}</Tooltip>);
        const val = data.dimensions[dim.dim1].values[dim.dim1Idx];
        const header = data.dimensions[dim.dim1].name + ' ' + val;
        return (
            <div id="disaster-analysis-data-container" className="container-fluid">
                <div className="row">
                    <div className="btn-group">
                        <OverlayTrigger placement="bottom" overlay={tooltip}>
                            <button id="disaster-back-button" onClick={()=> this.props.getData(this.props.analysisType.href, true)} className="btn btn-primary">
                                <i className="fa fa-arrow-left"/>
                            </button>
                        </OverlayTrigger>
                        <DownloadData/>
                        <MoreInfo/>
                    </div>
                </div>
                <div className="row">
                    <h4 style={{margin: 0}}>{hazardSet.title}</h4>
                </div>
                <div className="row">
                    <p>{hazardSet.purpose}</p>
                </div>
                <div id="disaster-chart-container" className="row">
                    <Panel className="chart-panel">
                        <Chart/>
                    </Panel>
                    {data.dimensions[dim.dim1].values.length - 1 === 0 ? (
                    <div className="slider-box">
                        <LabelResource uid={'chart_label_tab'} label={header} dimension={data.dimensions[dim.dim1]}/>
                    </div>
                    ) : (
                    <div>
                        <div className="slider-box">
                            <LabelResource uid={'chart_label_tab'} label={header} dimension={data.dimensions[dim.dim1]}/>
                            <Nouislider
                                range={{min: 0, max: data.dimensions[dim.dim1].values.length - 1}}
                                start={[dim.dim1Idx]}
                                step={1}
                                tooltips={false}
                                onChange={(idx) => this.props.setDimIdx('dim1Idx', Number.parseInt(idx[0]))}
                                pips= {{
                                    mode: 'steps',
                                    density: 20,
                                    format: {
                                        to: (value) => {
                                            let valF = data.dimensions[dim.dim1].values[value].split(" ")[0];
                                            return valF.length > 8 ? valF.substring(0, 8) + '...' : valF;
                                        },
                                        from: (value) => {
                                            return value;
                                        }
                                    }
                                }}/>
                          </div>
                        <hr/>
                    </div>
                    )}
                    <SummaryChart/>
                </div>
            </div>
        );
    },
    renderRiskAnalysisHeader(title, getAnalysis, rs, idx) {
        const tooltip = (<Tooltip id={"tooltip-abstract-" + idx} className="disaster">{'Show Abstract'}</Tooltip>);
        return (
          <OverlayTrigger placement="top" overlay={tooltip}>
          <div className="row">
            <div className="col-xs-10">
              <div className="disaster-analysis-title">{title}</div>
            </div>
            <div className="col-xs-2">
                <i className="pull-right fa fa-chevron-down"></i>
            </div>
          </div>
          </OverlayTrigger>
        );
    },
    renderRiskAnalysis() {
        const {analysisType = {}, getAnalysis} = this.props;
        return analysisType.riskAnalysis.map((rs, idx) => {
            const {title, fa_icon: faIcon, abstract} = rs.hazardSet;
            const tooltip = (<Tooltip id={"tooltip-icon-cat-" + idx} className="disaster">{'Analysis Data'}</Tooltip>);
            return (
              <div key={idx} className="row">
                  <div className="col-xs-1 text-center">
                      <OverlayTrigger placement="bottom" overlay={tooltip}>
                        <i className={'disaster-category fa ' + faIcon} onClick={()=> getAnalysis(rs.href)}></i>
                      </OverlayTrigger>
                  </div>
                  <div className="col-xs-11">
                    <Panel collapsible header={this.renderRiskAnalysisHeader(title, getAnalysis, rs, idx)}>
                        {abstract}
                        <br/>
                        <button className="btn btn-default pull-right" onClick={()=> getAnalysis(rs.href)}><i className="fa fa-bar-chart"/>&nbsp;{'Analysis Data'}</button>
                    </Panel>
                  </div>
              </div>
            );
        });
    },
    renderAnalysisTab() {
        const {hazardType = {}, analysisType = {}, getData: loadData} = this.props;
        return (hazardType.analysisTypes || []).map((type, idx) => {
            const {href, name, title, faIcon, description} = type;
            const active = name === analysisType.name;
            const tooltip = (<Tooltip id={"tooltip-icon-analysis-tab-" + idx} className="disaster">{description}</Tooltip>);
            return (
                <OverlayTrigger key={name} placement="bottom" overlay={tooltip}>
                    <li className={`text-center ${active ? 'active' : ''}`} onClick={() => loadData(href, true)}>
                        <a href="#" data-toggle="tab"><span> <i className={"fa fa-" + faIcon}></i>&nbsp;{title}</span></a>
                    </li>
                </OverlayTrigger>
            );
        });
    },
    renderHazard() {
        const {riskAnalysisData} = this.props;

        return (<div className={this.props.className}>
                <div className="disaster-header">
                  {riskAnalysisData.name ? (
                    <div className="container-fluid">
                        {this.renderAnalysisData()}
                    </div>
                    ) : (
                    <div className="container-fluid">
                        <ul id="disaster-analysis-menu" className="nav nav-pills">
                            {this.renderAnalysisTab()}
                        </ul>
                        <hr></hr>
                        <div id="disaster-analysis-container" className="disaster-analysis">
                            <div className="container-fluid">
                                {this.renderRiskAnalysis()}
                            </div>
                        </div>
                    </div>
                  )}
                </div>
            </div>
        );
    },
    render() {
        const {showHazard, getData: loadData} = this.props;
        return showHazard ? this.renderHazard() : (<Overview className={this.props.className} getData={loadData}/>);
    }
});

module.exports = connect(dataContainerSelector, {getAnalysis: getAnalysisData, getData, setDimIdx})(DataContainer);
