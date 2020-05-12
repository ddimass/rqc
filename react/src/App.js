import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { w3cwebsocket as W3CWebSocket } from "websocket";
import {length} from "@amcharts/amcharts4/.internal/core/utils/Iterator";
//188.72.76.54 101.100.20.10
const client = new W3CWebSocket('ws://188.72.76.54:8000/ws');
function compare(a, b) {
  if (a['dat'] > b['dat']) return 1;
  if (a['dat'] < b['dat']) return -1;
  return 0;
}
am4core.useTheme(am4themes_animated);

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {data1: []};
  }

  componentDidMount() {

    let chart = am4core.create("chartdiv", am4charts.XYChart);
    chart.paddingRight = 20;
    let data2 = [
        {dat: 0, mess: 0},
        {dat: 1, mess: -0.06855538345504619},
        {dat: 2, mess: -0.20785627268390527},
        {dat: 3, mess: -0.3367407359189887},
        {dat: 4, mess: -0.43759390824553923},
        {dat: 5, mess: -0.7081410511650416}
    ]
    chart.data = this.state.data1;
    chart.hiddenState.properties.opacity = 0;

    chart.padding(0, 0, 0, 0);

    chart.zoomOutButton.disabled = true;

    let dateAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    dateAxis.dataFields.category = "dat";
    dateAxis.renderer.grid.template.location = 0;

    let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.renderer.minWidth = 35;

    let series = chart.series.push(new am4charts.LineSeries());
    series.dataFields.categoryX = "dat";
    series.dataFields.valueY = "mess";

    series.tooltipText = "{valueY.value}";
    chart.cursor = new am4charts.XYCursor();

    let scrollbarX = new am4charts.XYChartScrollbar();
    scrollbarX.series.push(series);
    chart.scrollbarX = scrollbarX;
    this.setState({data1: [], chart1: chart});
    this.chart = chart;
  }

  componentWillUnmount() {
    if (this.chart) {
      this.chart.dispose();
    }
  }

  componentWillMount() {
    client.onopen = () => {
      console.log('WebSocket Client Connected');
      client.send('From socket');
    };
    client.onmessage = (message) => {
      client.send('From socket');
      let data1 = this.state.data1;
      let mess = JSON.parse(message.data);
      console.log(mess);
      //console.log(message.data);
      data1.push(mess);
      data1.sort(compare);
      let chart = this.state.chart1;
      chart.data = data1;
      this.setState({data1: data1, chart1: chart});
    };
    this.forceUpdate();
  }

  render() {
    return (
      <div id="chartdiv" style={{ width: "100%", height: "500px" }}></div>
    );
  }
}

export default App;
