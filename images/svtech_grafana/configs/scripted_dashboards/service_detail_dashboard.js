'use strict';

// accessible variables in this scope
var window, document, ARGS, $, jQuery, moment, kbn;

// Setup some variables
var dashboard;

// All url parameters are available via the ARGS object
var ARGS;

var hostname = '';
var servicename = '';
var datasource_live = 'default';
var livestatus_name = '';

if(!_.isUndefined(ARGS.host)) {
  hostname = ARGS.host;
}

if(!_.isUndefined(ARGS.service)) {
  servicename = ARGS.service;
}

if(!_.isUndefined(ARGS.reportds)) {
  datasource_live = ARGS.reportds;
}

if(!_.isUndefined(ARGS.livename)) {
  livestatus_name = ARGS.livename;
}
// Initialize a skeleton with nothing but a rows array and service object
dashboard = {
  panels : [],
};

dashboard.templating = {
  list: [
      {
        "hide": 0,
        "label": "InfluxDB",
        "name": "influx",
        "options": [],
        "query": "influxdb",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "type": "datasource"
      },
      {
      	"allValue": null,
        "current": {
          "text": "Interface-check-command",
          "value": "Interface-check-command"
        },
        "datasource": datasource_live,
        "definition": "SELECT services.check_command FROM "+ livestatus_name +" WHERE host_name = "+ hostname +" AND display_name ~ "+ servicename +";",
        "hide": 2,
        "includeAll": false,
        "label": "command",
        "multi": false,
        "name": "command",
        "options": [],
        "query": "SELECT services.check_command FROM "+ livestatus_name +" WHERE host_name = "+ hostname +" AND display_name ~ "+ servicename +";",
        "refresh": 1,
        "regex": "check_(.*)\\!",
        "skipUrlSync": false,
        "sort": 1,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      }
  ]
};

function add_livestatus_panel(rows, datasource, host, service, livestatus_name) {
  rows.push({
  "columns": [],
  "datasource": datasource,
  "fontSize": "100%",
  "gridPos": {
    "h": 18,
    "w": 11,
    "x": 0,
    "y": 0
  },
  "id": 2,
  "links": [],
  "pageSize": null,
  "scroll": true,
  "showHeader": true,
  "sort": {
    "col": 0,
    "desc": true
  },
  "styles": [
    {
      "alias": "Service",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)",
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "display_name",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Check Command",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "check_command_expanded",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Current Status",
      "colorMode": "cell",
      "colors": [
        "rgba(50, 172, 45, 0.97)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(245, 54, 54, 0.9)",
        "#ff9933"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "state",
      "thresholds": [
        "1",
        "2",
        "3",
        "4"
      ],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "OK",
          "value": "0"
        },
        {
          "text": "WARNING",
          "value": "1"
        },
        {
          "text": "CRITICAL",
          "value": "2"
        },
        {
          "text": "UNKNOWN",
          "value": "3"
        },
        {
          "text": "PENDING",
          "value": "4"
        }
      ]
    },
    {
      "alias": "State Type",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "state_type",
      "thresholds": [],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "SOFT",
          "value": "0"
        },
        {
          "text": "HARD",
          "value": "1"
        }
      ]
    },
    {
      "alias": "Notification Enable",
      "colorMode": "cell",
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "notifications_enabled",
      "thresholds": [
        "0.5",
        "1"
      ],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "NO",
          "value": "0"
        },
        {
          "text": "YES",
          "value": "1"
        }
      ]
    },
    {
      "alias": "Status Information",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "plugin_output",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Status Detail Information",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "long_plugin_output",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Last Check Time",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "last_check",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Last State Change",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "last_state_change",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Performance Data (raw data)",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "perf_data",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Process Pef. Data",
      "colorMode": "cell",
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "process_performance_data",
      "thresholds": [
        "0.5",
        " 1"
      ],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "NO",
          "value": "0"
        },
        {
          "text": "YES",
          "value": "1"
        }
      ]
    },
    {
      "alias": "Check Type",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "check_type",
      "thresholds": [],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "Active",
          "value": "0"
        },
        {
          "text": "Passive",
          "value": "1"
        }
      ]
    },
    {
      "alias": "Last Hard State",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "last_hard_state",
      "thresholds": [],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "OK",
          "value": "0"
        },
        {
          "text": "WARNING",
          "value": "1"
        },
        {
          "text": "CRITICAL",
          "value": "2"
        },
        {
          "text": "UNKNOWN",
          "value": "3"
        },
        {
          "text": "PENDING",
          "value": "4"
        }
      ]
    },
    {
      "alias": "Last Hard State Change",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "last_hard_state_change",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Last Notification",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "last_notification",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Current Notification Number",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "current_notification_number",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Next Check",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "next_check",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Checked",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "has_been_checked",
      "thresholds": [],
      "type": "string",
      "unit": "short",
      "valueMaps": [
        {
          "text": "NO",
          "value": "0"
        },
        {
          "text": "YES",
          "value": "1"
        }
      ]
    },
    {
      "alias": "Check Period",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "check_period",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Check Interval",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "check_interval",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Retry Interval",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "retry_interval",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Notification Interval",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 0,
      "mappingType": 1,
      "pattern": "notification_interval",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Latency",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 5,
      "mappingType": 1,
      "pattern": "latency",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Execution Time",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 5,
      "mappingType": 1,
      "pattern": "execution_time",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Groups",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "groups",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    },
    {
      "alias": "Host Name",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "host_name",
      "thresholds": [],
      "type": "string",
      "unit": "short"
    },
	{
      "alias": "Livestatus Back-end",
      "colorMode": null,
      "colors": [
        "rgba(245, 54, 54, 0.9)",
        "rgba(237, 129, 40, 0.89)",
        "rgba(50, 172, 45, 0.97)"
      ],
      "dateFormat": "YYYY-MM-DD HH:mm:ss",
      "decimals": 2,
      "mappingType": 1,
      "pattern": "livestatus_name",
      "thresholds": [],
      "type": "number",
      "unit": "short"
    }
  ],
  "targets": [
    {
      "hide": false,
      "query": {
        "datasource": [
          "services",
          "SELECT",
          "display_name",
          "host_name",
          "check_command_expanded",
          "state",
          "state_type",
          "notifications_enabled",
          "plugin_output",
          "long_plugin_output",
          "last_check",
          "last_state_change",
          "perf_data",
          "process_performance_data",
          "check_type",
          "last_hard_state",
          "last_hard_state_change",
          "last_notification",
          "current_notification_number",
          "next_check",
          "has_been_checked",
          "check_period",
          "check_interval",
          "retry_interval",
          "notification_interval",
          "latency",
          "execution_time",
          "groups",
          "FROM",
          livestatus_name
        ],
        "hostFilter": [],
        "serviceFilter": []
      },
      "refId": "A",
      "segments": [
        "SELECT",
        "display_name",
        "host_name",
        "check_command_expanded",
        "state",
        "state_type",
        "notifications_enabled",
        "plugin_output",
        "long_plugin_output",
        "last_check",
        "last_state_change",
        "perf_data",
        "process_performance_data",
        "check_type",
        "last_hard_state",
        "last_hard_state_change",
        "last_notification",
        "current_notification_number",
        "next_check",
        "has_been_checked",
        "check_period",
        "check_interval",
        "retry_interval",
        "notification_interval",
        "latency",
        "execution_time",
        "groups",
        "FROM",
        livestatus_name,
        "WHERE",
		"host_name",
        "=",
        host,
        "AND",
        "display_name",
        "=",
        service,
        "*"
      ],
      "target": "services",
      "type": "timeserie"
    }
  ],
  "title": "Detail Service Information",
  "transform": "table",
  "type": "icinga2-report-panel-transposed"
  })
}

function add_ping_service(rows, hostname) {
	rows.push({
  "aliasColors": {
    "PL": "#bf1b00",
    "RTA": "#70dbed"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "description": "",
  "fill": 5,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [
    {
      "type": "dashboard"
    }
  ],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": null,
  "repeatDirection": "h",
  "seriesOverrides": [
    {
      "alias": "PL",
      "yaxis": 2
    }
  ],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "RTA",
      "bucketAggs": [
        {
          "field": "@timestamp",
          "id": "2",
          "settings": {
            "interval": "auto",
            "min_doc_count": 0,
            "trimEdges": 0
          },
          "type": "date_histogram"
        }
      ],
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "ping4",
      "metrics": [
        {
          "field": "select field",
          "id": "1",
          "type": "count"
        }
      ],
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT last(\"value\") FROM \"ping4\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'rta') AND $timeFilter GROUP BY time($__interval) fill(previous)",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "rta"
        }
      ],
      "timeField": "@timestamp",
      "rawQuery": false
    },
    {
      "alias": "PL",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "ping4",
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT mean(\"value\") FROM \"ping4\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'pl') AND $timeFilter GROUP BY time($__interval) fill(null)",
      "rawQuery": false,
      "refId": "B",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "pl"
        }
      ]
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "Ping4",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "transparent": false,
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "s",
      "label": "RTA",
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    },
    {
      "decimals": 0,
      "format": "percent",
      "label": "PL",
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_CPU_load(rows, hostname, servicename) {
	rows.push({
  "datasource": "$influx",
  "aliasColors": {
    "CPU Load": "#eab839",
    "CPU Load (%)": "#447ebc",
    "CPU Load RE0": "#0a437c",
    "CPU Load RE1": "#5195ce",
    "Last": "#eab839"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "decimals": null,
  "description": "",
  "fill": 5,
  "fillGradient": 0,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "hideEmpty": false,
    "hideZero": false,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "maxPerRow": 2,
  "nullPointMode": "null",
  "options": {
    "dataLinks": []
  },
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": null,
  "seriesOverrides": [
    {
      "alias": "CPU Load (%)",
      "yaxis": 1
    }
  ],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "CPU Load $tag_metric",
      "bucketAggs": [
        {
          "field": "@timestamp",
          "id": "2",
          "settings": {
            "interval": "auto",
            "min_doc_count": 0,
            "trimEdges": 0
          },
          "type": "date_histogram"
        }
      ],
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "metric"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "snmp",
      "metrics": [
        {
          "field": "select field",
          "id": "1",
          "type": "count"
        }
      ],
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT last(\"value\") FROM \"snmp\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" =~ /^CPU.*RE.*$/ AND \"service\" = '"+ servicename + "') AND $timeFilter GROUP BY time($__interval), \"metric\" fill(previous)",
      "rawQuery": false,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=~",
          "value": "/^CPU.*RE.*$/"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ],
      "timeField": "@timestamp"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeRegions": [],
  "timeShift": null,
  "title": "CPU LOAD",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "percent",
      "label": "",
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_juniper_memory(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {
    "Memory RE0": "#3f6833",
    "Memory RE1": "#7eb26d"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "fill": 5,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "max": true,
    "min": true,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "Memory $tag_metric",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "metric"
          ],
          "type": "tag"
        },
        {
          "params": [
            "0"
          ],
          "type": "fill"
        }
      ],
      "measurement": "snmp",
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT max(\"value\") FROM \"snmp\" WHERE (\"hostname\" = '" + hostname + "' AND \"service\" = '" + servicename + "' AND \"metric\" =~ /^MEM.*RE.*$/) AND $timeFilter GROUP BY time($__interval), \"metric\" fill(0)",
      "rawQuery": false,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "max"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=~",
          "value": "/^MEM.*RE.*$/"
        }
      ],
      "target": "select metric",
      "type": "timeserie"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "MEMORY",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "format": "percent",
      "label": null,
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_juniper_temperature(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {
    "TEMPERATURE (C)": "#e24d42",
    "Temperature": "#052b51",
    "Temperature ACX": "#890f02",
    "Temperature RE0": "#890f02",
    "Temperature RE1": "#e0752d",
    "Temperature TEMP_RE0": "#e24d42",
    "Temperature TEMP_RE1": "#890f02"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "decimals": 0,
  "description": "",
  "fill": 5,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "hideEmpty": false,
    "hideZero": false,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "sideWidth": null,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": null,
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "Temperature $tag_metric",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "metric"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "snmp",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "C",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "max"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=~",
          "value": "/TEMP.*RE.*/"
        }
      ],
      "target": "select metric",
      "type": "timeserie"
    },
    {
      "alias": "Temperature $tag_metric",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "metric"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "snmp",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "max"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=~",
          "value": "/TEMP.*Chassis.*/"
        }
      ],
      "target": "select metric",
      "type": "timeserie"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "TEMPERATURE",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "cumulative"
  },
  "transparent": false,
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": 0,
      "format": "celsius",
      "label": "",
      "logBase": 1,
      "max": "120",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_cpu_load_fpc(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {
    "CPU Load": "#eab839",
    "CPU Load (%)": "#447ebc",
    "CPU Load RE0": "#0a437c",
    "CPU Load RE1": "#5195ce",
    "Last": "#eab839"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "decimals": null,
  "description": "",
  "fill": 5,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "hideEmpty": false,
    "hideZero": false,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [
    {
      "alias": "CPU Load (%)",
      "yaxis": 1
    }
  ],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "CPU Load $tag_service",
      "bucketAggs": [
        {
          "field": "@timestamp",
          "id": "2",
          "settings": {
            "interval": "auto",
            "min_doc_count": 0,
            "trimEdges": 0
          },
          "type": "date_histogram"
        }
      ],
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "service"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "snmp",
      "metrics": [
        {
          "field": "select field",
          "id": "1",
          "type": "count"
        }
      ],
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT last(\"value\") FROM \"snmp\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'CPU_FPC' AND \"service\" = '" + servicename + "') AND $timeFilter GROUP BY time($__interval), \"service\" fill(previous)",
      "rawQuery": false,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "CPU_FPC"
        },        
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ],
      "timeField": "@timestamp"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "CPU LOAD FPC",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "percent",
      "label": "",
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_mem_load_fpc(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {
    "CPU Load": "#eab839",
    "CPU Load (%)": "#447ebc",
    "CPU Load RE0": "#0a437c",
    "CPU Load RE1": "#5195ce",
    "Last": "#eab839"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "decimals": null,
  "description": "",
  "fill": 5,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "hideEmpty": false,
    "hideZero": false,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [
    {
      "alias": "CPU Load (%)",
      "yaxis": 1
    }
  ],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "MEM Load $tag_service",
      "bucketAggs": [
        {
          "field": "@timestamp",
          "id": "2",
          "settings": {
            "interval": "auto",
            "min_doc_count": 0,
            "trimEdges": 0
          },
          "type": "date_histogram"
        }
      ],
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "service"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "snmp",
      "metrics": [
        {
          "field": "select field",
          "id": "1",
          "type": "count"
        }
      ],
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT last(\"value\") FROM \"snmp\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'MEM_FPC' AND \"service\" = '" + servicename + "') AND $timeFilter GROUP BY time($__interval), \"service\" fill(previous)",
      "rawQuery": false,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "MEM_FPC"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        },
      ],
      "timeField": "@timestamp"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "MEM LOAD FPC",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "percent",
      "label": "",
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_temperature_fpc(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {
    "CPU Load": "#eab839",
    "CPU Load (%)": "#447ebc",
    "CPU Load RE0": "#0a437c",
    "CPU Load RE1": "#5195ce",
    "Last": "#eab839",
    "Temperature FPCTemp-FPC2": "#bf1b00",
    "Temperature FPCTemp-FPC3": "#629e51",
    "Temperature FPCTemp-FPC7": "#e0752d"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "decimals": null,
  "description": "",
  "fill": 2,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "height": "",
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": false,
    "current": true,
    "hideEmpty": false,
    "hideZero": false,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [],
  "minSpan": 12,
  "nullPointMode": "null",
  "percentage": true,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": "Temperature $tag_service",
      "bucketAggs": [
        {
          "field": "@timestamp",
          "id": "2",
          "settings": {
            "interval": "auto",
            "min_doc_count": 0,
            "trimEdges": 0
          },
          "type": "date_histogram"
        }
      ],
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "service"
          ],
          "type": "tag"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": "snmp",
      "metrics": [
        {
          "field": "select field",
          "id": "1",
          "type": "count"
        }
      ],
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT last(\"value\") FROM \"snmp\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'TEMP_FPC' AND \"service\" = '" + servicename + "') AND $timeFilter GROUP BY time($__interval), \"service\" fill(previous)",
      "rawQuery": false,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "TEMP_FPC"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ],
      "timeField": "@timestamp"
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "TEMPERATURE FPC",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "celsius",
      "label": "",
      "logBase": 1,
      "max": "100",
      "min": "0",
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}


function add_bandwidth_total(rows, hostname) {
	rows.push({
  "aliasColors": {},
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "fill": 1,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [
    {
      "keepTime": false,
      "type": "dashboard"
    }
  ],
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": hostname + "-total-InBit",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "Interface-check-command",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "sum"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "in_bits"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "!~",
          "value": "/.*.ae.*./"
        }
      ],
      "query": "SELECT sum(\"value\") FROM \"Interface-check-command\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'in_bits' AND \"service\" !~ /.*.ae.*./) AND $timeFilter GROUP BY time($__interval) fill(previous)",
      "rawQuery": false
    },
    {
      "alias": hostname + "-total-OutBit",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "Interface-check-command",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "B",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "sum"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "out_bits"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "!~",
          "value": "/.*.ae.*./"
        }
      ],
      "query": "SELECT sum(\"value\") FROM \"Interface-check-command\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'out_bits' AND \"service\" !~ /.*.ae.*./) AND $timeFilter GROUP BY time($__interval) fill(previous)",
      "rawQuery": false
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "BandwidthTotal",
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "bytes",
      "label": "",
      "logBase": 1,
      "max": null,
      "min": 0,
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_bandwidth_ifcheck(rows, hostname, servicename) {
	rows.push({
  "aliasColors": {},
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "datasource": "$influx",
  "fill": 1,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "sortDesc": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [
    {
      "includeVars": false,
      "keepTime": false,
      "type": "dashboard"
    }
  ],
  "minSpan": 1,
  "nullPointMode": "null",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": "interface",
  "repeatDirection": "h",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": hostname + "-" + servicename + "-InBit",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "Interface-check-command",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "in_bits"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ],
      "query": "SELECT mean(\"value\") FROM \"Interface-check-command\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'in_bits' AND \"service\" = " + servicename + ") AND $timeFilter GROUP BY time($__interval) fill(previous)",
      "rawQuery": false
    },
    {
      "alias": hostname + "-" + servicename + "-OutBit",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "previous"
          ],
          "type": "fill"
        }
      ],
      "measurement": "Interface-check-command",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "B",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "out_bits"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ],
      "query": "SELECT mean(\"value\") FROM \"Interface-check-command\" WHERE (\"hostname\" = '" + hostname + "' AND \"metric\" = 'out_bits' AND \"service\" = " + servicename + ") AND $timeFilter GROUP BY time($__interval) fill(previous)",
      "rawQuery": false
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeShift": null,
  "title": "BandwidthSpecific-" + servicename,
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "bytes",
      "label": "",
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 1,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  },
  "fillGradient": 0,
  "timeRegions": [],
  "decimals": 2
})
}

function add_default_panel(rows, hostname, servicename){
	rows.push(
	{
		"datasource": "$influx",
		"aliasColors": {
			"PL": "#bf1b00",
			"RTA": "#70dbed"
		},
		"bars": false,
		"dashLength": 10,
		"dashes": false,
		"description": "",
		"fill": 5,
		"fillGradient": 0,
		"gridPos": {
			"h": 16,
			"w": 13,
			"x": 11,
			"y": 2
		},
		"height": "",
		"id": 6,
		"legend": {
			"alignAsTable": true,
			"avg": false,
			"current": true,
			"max": true,
			"min": true,
			"rightSide": false,
			"show": true,
			"total": false,
			"values": true
		},
		"lines": true,
		"linewidth": 1,
		"links": [
		{
		  "url": "/"
		}
		],
		"maxPerRow": 2,
		"nullPointMode": "null",
		"options": {
		"dataLinks": []
		},
		"percentage": false,
		"pointradius": 5,
		"points": false,
		"renderer": "flot",
		"repeat": null,
		"repeatDirection": "h",
		"seriesOverrides": [
		{
		  "alias": "PL",
		  "yaxis": 2
		}
		],
		"spaceLength": 10,
		"stack": false,
		"steppedLine": false,
		"targets": [
		{
		  "alias": "",
		  "bucketAggs": [
		    {
		      "field": "@timestamp",
		      "id": "2",
		      "settings": {
		        "interval": "auto",
		        "min_doc_count": 0,
		        "trimEdges": 0
		      },
		      "type": "date_histogram"
		    }
		  ],
		  "dsType": "influxdb",
		  "groupBy": [
		    {
		      "params": [
		        "$__interval"
		      ],
		      "type": "time"
		    },
		    {
		      "params": [
		        "metric"
		      ],
		      "type": "tag"
		    },
		    {
		      "params": [
		        "service"
		      ],
		      "type": "tag"
		    },
		    {
		      "params": [
		        "previous"
		      ],
		      "type": "fill"
		    }
		  ],
		  "hide": false,
		  "measurement": "/^$command$/",
		  "metrics": [
		    {
		      "field": "select field",
		      "id": "1",
		      "type": "count"
		    }
		  ],
		  "orderByTime": "ASC",
		  "policy": "default",
		  "query": "SELECT mean(\"value\") FROM \"ping4\" WHERE (\"metric\" = 'pl' AND \"hostname\" = '" + hostname + "') AND $timeFilter GROUP BY time($interval) fill(null)",
		  "refId": "A",
		  "resultFormat": "time_series",
		  "select": [
		    [
		      {
		        "params": [
		          "value"
		        ],
		        "type": "field"
		      },
		      {
		        "params": [],
		        "type": "max"
		      }
		    ]
		  ],
		  "tags": [
		    {
		      "key": "hostname",
		      "operator": "=",
		      "value": hostname
		    },
		    {
		      "condition": "AND",
		      "key": "service",
		      "operator": "=",
		      "value": servicename
		    }
		  ],
		  "timeField": "@timestamp"
		}
		],
		"thresholds": [],
		"timeFrom": null,
		"timeRegions": [],
		"timeShift": null,
		"title": "Graph of \"" + servicename + "\" on " + hostname,
		"tooltip": {
		"shared": true,
		"sort": 0,
		"value_type": "individual"
		},
		"type": "graph",
		"xaxis": {
			"buckets": null,
			"mode": "time",
			"name": null,
			"show": true,
			"values": []
		},
		"yaxes": [
		{
		  "decimals": null,
		  "format": "none",
		  "label": "RTA",
		  "logBase": 1,
		  "max": null,
		  "min": null,
		  "show": true
		},
		{
		  "decimals": 0,
		  "format": "none",
		  "label": "PL",
		  "logBase": 1,
		  "max": "100",
		  "min": "0",
		  "show": true
		}
		],
		"yaxis": {
			"align": false,
			"alignLevel": null
		}
	}
	)
};

function add_button_check(rows, datasource, live_name, hostname, servicename){
	rows.push({
  "content": "<div align=\"center\">\n<button onClick=\"send_command('SCHEDULE_FORCED_SVC_CHECK', host, service, livestatus_name)\" style=\"color: black\">Force Check</button>\n<button onClick=\"send_command('ENABLE_SVC_NOTIFICATIONS', host, service, livestatus_name)\" style=\"color: black\">Enable Notification</button>\n<button onClick=\"send_command('DISABLE_SVC_NOTIFICATIONS', host, service, livestatus_name)\" style=\"color: black\">Disable Notification</button>\n<script type=\"text/javascript\">\n  var host = '" + hostname + "';\n  var service = '" + servicename + "';\n  var livestatus_name = '" + live_name + "';\n  var datasource = '" + datasource + "';\nfunction getURL() {\n    source_url = window.location;\n}\ngetURL();\nfunction send_command(type, host, service, livestatus_name) {\n  //Get the url datasource in grafana - Start\n  var r = confirm(\"Do you want to send the '\" + type + \"' command to livestatus ?\");\n  if (r == true) {\n    var req = new XMLHttpRequest();\n    req.open(\"GET\", \"/grafana/api/datasources/name/\" + datasource, false);\n    req.send(null);\n    console.log(req.status);\n    if (req.status == \"200\") {\n      var obj = JSON.parse(req.responseText);\n      var url = \"\";\n      url = source_url.protocol + \"//\" + source_url.host + \"/grafana/send_request/api/v1/\" + obj.name + \"/command?type=\" + encodeURIComponent(type) + \"&host=\" + encodeURIComponent(host) + \"&service=\" + encodeURIComponent(service) + \"&livename=\" + encodeURIComponent(livestatus_name);\n      console.log(url);\n      req.open(\"GET\", url, true);\n      req.addEventListener('load', function(){\n        console.log(req.status);\n        console.log(req.responseText);\n        setTimeout(continueExecution, 1000);\n      });\n      req.send(null);\n    }\n    else {\n      console.log(\"Error\");\n    }\n  }\n}\nfunction continueExecution() {\n  history.go(0);\n}\n</script>",

  "gridPos": {
    "h": 2,
    "w": 13,
    "x": 11,
    "y": 0
  },
  "id": 4,
  "links": [],
  "mode": "html",
  "title": "ACTION",
  "type": "text"
})
}

function add_ifcrc_panel(rows, hostname, servicename) {
    rows.push({
  "datasource": "$influx",
  "aliasColors": {
    "ME_PNP018AGG01_RE0-ae0-CRC": "dark-red",
    "ME_PT101RRT_RE0-xe-7/2/3-CRC": "dark-orange"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "sortDesc": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [
    {
      "url": "/"
    }
  ],
  "maxPerRow": 4,
  "nullPointMode": "null",
  "options": {
    "dataLinks": []
  },
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": "interface",
  "repeatDirection": "h",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": hostname + "-$tag_service",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "service"
          ],
          "type": "tag"
        },
        {
          "params": [
            "none"
          ],
          "type": "fill"
        }
      ],
      "measurement": "snmp",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "IfCRC"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ]
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeRegions": [],
  "timeShift": null,
  "title": servicename,
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "short",
      "label": "",
      "logBase": 2,
      "max": null,
      "min": null,
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 2,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

function add_module_temp(rows, hostname, servicename) {
    rows.push({
  "datasource": "$influx",
  "aliasColors": {
    "ME_PT101RRT_RE0-xe-7/2/3-CRC": "dark-red"
  },
  "bars": false,
  "dashLength": 10,
  "dashes": false,
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 16,
    "w": 13,
    "x": 11,
    "y": 2
  },
  "id": 6,
  "legend": {
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "max": true,
    "min": true,
    "rightSide": false,
    "show": true,
    "sortDesc": true,
    "total": false,
    "values": true
  },
  "lines": true,
  "linewidth": 1,
  "links": [
    {
      "url": "/"
    }
  ],
  "maxPerRow": 4,
  "nullPointMode": "null",
  "options": {
    "dataLinks": []
  },
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "repeat": "interface",
  "repeatDirection": "h",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": false,
  "steppedLine": false,
  "targets": [
    {
      "alias": hostname + "-$tag_service",
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "$__interval"
          ],
          "type": "time"
        },
        {
          "params": [
            "service"
          ],
          "type": "tag"
        },
        {
          "params": [
            "none"
          ],
          "type": "fill"
        }
      ],
      "measurement": "snmp",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": [
        {
          "key": "hostname",
          "operator": "=",
          "value": hostname
        },
        {
          "condition": "AND",
          "key": "metric",
          "operator": "=",
          "value": "ModuleTemp"
        },
        {
          "condition": "AND",
          "key": "service",
          "operator": "=",
          "value": servicename
        }
      ]
    }
  ],
  "thresholds": [],
  "timeFrom": null,
  "timeRegions": [],
  "timeShift": null,
  "title": "ModuleTemperature-" + servicename,
  "tooltip": {
    "shared": true,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": null,
    "mode": "time",
    "name": null,
    "show": true,
    "values": []
  },
  "yaxes": [
    {
      "decimals": null,
      "format": "celsius",
      "label": "",
      "logBase": 2,
      "max": null,
      "min": null,
      "show": true
    },
    {
      "format": "short",
      "label": null,
      "logBase": 2,
      "max": null,
      "min": null,
      "show": true
    }
  ],
  "yaxis": {
    "align": false,
    "alignLevel": null
  }
})
}

// Set a title
dashboard.title = 'Service Information Detail';

dashboard.time = {
  from: "now-6h",
  to: "now"
};


//Push data to dashboard
//Push data from livestatus - Start
add_livestatus_panel(dashboard.panels, datasource_live, hostname, servicename, livestatus_name);
add_button_check(dashboard.panels, datasource_live, livestatus_name, hostname, servicename);
//Push data from livestatus - End
//add_ping_service(dashboard.panels, influxds, hostname)
//add_CPU_load(dashboard.panels, influxds, hostname)
//add_juniper_memory(dashboard.panels, influxds, hostname)
//add_juniper_temperature(dashboard.panels, influxds, hostname)
//add_cpu_load_fpc(dashboard.panels, influxds, hostname)
//add_mem_load_fpc(dashboard.panels, influxds, hostname)
//add_temperature_fpc(dashboard.panels, influxds, hostname)
//add_bandwidth_total(dashboard.panels, influxds, hostname)
//add_bandwidth_ifcheck(dashboard.panels, influxds, hostname, servicename)
if (servicename == "ping4") {
	add_ping_service(dashboard.panels, hostname)
}
else if (servicename.includes("IfCheck")) {
	add_bandwidth_ifcheck(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("IfCRC")) {
    add_ifcrc_panel(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("ModuleTemp")) {
    add_module_temp(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("Juniper") && servicename.includes("CPU")) {
    add_CPU_load(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("Juniper") && (servicename.includes("MEM") || servicename.includes("Memory"))) {
	add_juniper_memory(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("Juniper") && (servicename.includes("TEMP") || servicename.includes("Temperature"))) {
	add_juniper_temperature(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("FPC") && servicename.includes("MEM")) {
	add_mem_load_fpc(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("FPC") && servicename.includes("CPU")) {
	add_cpu_load_fpc(dashboard.panels, hostname, servicename)
}
else if (servicename.includes("FPC") && (servicename.includes("TEMP") || servicename.includes("Temperature"))) {
	add_temperature_fpc(dashboard.panels, hostname, servicename)
}
else {
	add_default_panel(dashboard.panels, hostname, servicename)
}
return dashboard;