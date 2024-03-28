System.register(["./css/query-editor.css!", "lodash", "./plugins/simple-json-datasource/module"], function (_export, _context) {
  "use strict";

  var _, BaseDatasource, BaseQueryCtrl, BaseConfigCtrl, BaseQueryOptionsCtrl, BaseAnnotationsQueryCtrl;

  return {
    setters: [function (_cssQueryEditorCss) {}, function (_lodash) {
      _ = _lodash.default;
    }, function (_pluginsSimpleJsonDatasourceModule) {
      BaseDatasource = _pluginsSimpleJsonDatasourceModule.Datasource;
      BaseQueryCtrl = _pluginsSimpleJsonDatasourceModule.QueryCtrl;
      BaseConfigCtrl = _pluginsSimpleJsonDatasourceModule.ConfigCtrl;
      BaseQueryOptionsCtrl = _pluginsSimpleJsonDatasourceModule.QueryOptionsCtrl;
      BaseAnnotationsQueryCtrl = _pluginsSimpleJsonDatasourceModule.AnnotationsQueryCtrl;
    }],
    execute: function () {
      function _classCallCheck(instance, Constructor) {
        if (!(instance instanceof Constructor)) {
          throw new TypeError("Cannot call a class as a function");
        }
      }

      function _defineProperties(target, props) {
        for (var i = 0; i < props.length; i++) {
          var descriptor = props[i];
          descriptor.enumerable = descriptor.enumerable || false;
          descriptor.configurable = true;
          if ("value" in descriptor) descriptor.writable = true;
          Object.defineProperty(target, descriptor.key, descriptor);
        }
      }

      function _createClass(Constructor, protoProps, staticProps) {
        if (protoProps) _defineProperties(Constructor.prototype, protoProps);
        if (staticProps) _defineProperties(Constructor, staticProps);
        return Constructor;
      }

      function _possibleConstructorReturn(self, call) {
        if (call && (typeof call === "object" || typeof call === "function")) {
          return call;
        }

        if (!self) {
          throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
        }

        return self;
      }

      function _inherits(subClass, superClass) {
        if (typeof superClass !== "function" && superClass !== null) {
          throw new TypeError("Super expression must either be null or a function");
        }

        subClass.prototype = Object.create(superClass && superClass.prototype, {
          constructor: {
            value: subClass,
            enumerable: false,
            writable: true,
            configurable: true
          }
        });
        if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
      }

      let Icinga2ReportQueryCtrl = function (_BaseQueryCtrl) {
        var current_segments
        var current_index
        var list_special_index = []
        var onclick_segment 
        var SpecialSegment = ['WHERE', 'GROUP BY', 'Host Filter:', 'Service Filter:']
        _inherits(Icinga2ReportQueryCtrl, _BaseQueryCtrl);

        function Icinga2ReportQueryCtrl($scope, $injector, uiSegmentSrv) {
          var _this;

          _classCallCheck(this, Icinga2ReportQueryCtrl);

          _this = _possibleConstructorReturn(this, (Icinga2ReportQueryCtrl.__proto__ || Object.getPrototypeOf(Icinga2ReportQueryCtrl)).call(this, $scope, $injector));
          _this.uiSegmentSrv = uiSegmentSrv;
          _this.segments = _.map(_this.target.segments, s => _this.uiSegmentSrv.newSegment(s));

          _this.segments.push(_this.uiSegmentSrv.newSegment('*'));

          _this.columns = [];
          return _this;
        }

        _createClass(Icinga2ReportQueryCtrl, [{
          key: "getSegments",
          value: function getSegments(index = 0) {

            return this.datasource.doRequest({
              url: this.datasource.url + '/segments',
              data: {
                source: this.target.target,
                segments: _.map(this.segments, 'value'),
                index: index
              },
              method: 'POST'
            }).then(result => {
              this.columns[index] = result.data.values;
              if (this.segments.length <= index) {
                this.segments.push(this.uiSegmentSrv.newSegment(this.columns[index][0]));
                this.target.segments = _.map(this.segments, 'value');
                // this.segments.push(this.uiSegmentSrv.newSegment('*')); // this.segmentValueChanged(null, index)
                this.segments.splice(index + 1, 0, this.uiSegmentSrv.newSegment('*'));
              }

              return _.map(result.data.values, s => this.uiSegmentSrv.newSegment(s));
            });
          }
        }, {
          key: "segmentValueChanged",
          value: function segmentValueChanged(segment, $index) {
            var begin_index
            var next_SpecialSegment_index
            var count_index
            var operators = ['=', '!=', '~', '!~', '~~', '!~~', '|', ':']
            console.log(segment.value)
            // if (_.includes(['=', '!=', '~', '!~', '~~', '!~~', ')', '('], segment.value)) {

            // Check value of changed segment
            // Case 1 : value in ['=', '!=', '~', '!~', '~~', '!~~'] --> Add 2 '*'
            if (operators.includes(segment.value) ) {
              this.segments.splice($index + 1, 0, this.uiSegmentSrv.newSegment('*'));
              this.getSegments($index + 1);
            } 

            // Case 2: value == '*' -> remove
            else if (segment.value == '*') {
              this.getSegments($index + 1);
              for (var i = 0; i < list_special_index.length; i ++){
                // Case 2.1: Have 1 Group or is last Group -> remove from ($index + 1) to end
                if(list_special_index.length == 1 || $index == list_special_index[list_special_index.length - 1]){
                  this.segments.splice($index + 1);
                  this.getSegments($index + 1);
                }
                // Case 2.2: Remove whole segments in  sellected Middle Group 
                else if (list_special_index.length > 2 && $index == list_special_index[i] || $index == list_special_index[0]){
                  begin_index = $index
                  count_index = list_special_index[i + 1] - begin_index
                  this.segments.splice(begin_index, count_index);
                  this.getSegments($index + 1);
                }
                // Case 2.3: Remove segments in Middle Group. Remove from [sellected segments --> next Middle Group]
                else if ($index > list_special_index[i - 1] && $index < list_special_index[i]){
                  this.segments.splice($index, list_special_index[i] - $index , this.uiSegmentSrv.newSegment('*'));
                  this.getSegments($index + 1);
                }
                // Case 2.4: Remove segments in Last Group. Remove from [sellected segments --> end]
                else if ($index > list_special_index[list_special_index.length - 1]){
                  this.segments.splice($index, list_special_index[i] , this.uiSegmentSrv.newSegment('*'));
                  this.getSegments($index + 1);
                }
              }
            }
            else if (segment.value == '--DELETE--') {
              this.segments.splice($index, 1);
              this.getSegments($index);
            }
            // Case 3: Other Case. --> Add 1 '*'
            else if (segment.value != '*') {
              this.getSegments($index + 1);
              if ($index < this.segments.length - 2){ // Trường hợp muốn chỉnh sửa ở giữa -> sinh ra dấu "*" tại sau index được chọn
                this.segments.splice($index + 1, 0, this.uiSegmentSrv.newSegment('*'));
              }
            }
            this.target.segments = _.map(this.segments, 'value');
          }
        }, {
          key: "getAltSegments",
          value: function getAltSegments(index) {
            list_special_index = []
            current_segments = this.segments.slice(0)
            current_index = index
            onclick_segment = current_segments[index].value

            for(var i = 0; i < current_segments.length; i ++){
              if (SpecialSegment.includes(current_segments[i].value) == true){
                list_special_index.push(i)
              }
            }

            if (this.columns[index]) {
              return Promise.resolve(_.map(this.columns[index], s => this.uiSegmentSrv.newSegment(s)));
            }

            return this.getSegments(index);
          }
        }, {
          key: "handleSourceChanged",
          value: function handleSourceChanged() {
            this.segments.splice(0);
            this.getSegments();
          }
        }, {
          key: "isSpecialSegment",
          value: function isSpecialSegment(segment) {
            return segment.value == 'WHERE' || segment.value == 'GROUP BY' || segment.value == 'Host Filter:' || segment.value == 'Service Filter:';
          }
        }]);

        return Icinga2ReportQueryCtrl;
      }(BaseQueryCtrl);

      let Icinga2ReportDatasource = function (_BaseDatasource) {
        _inherits(Icinga2ReportDatasource, _BaseDatasource);

        function Icinga2ReportDatasource(instanceSettings, $q, backendSrv, templateSrv) {
          _classCallCheck(this, Icinga2ReportDatasource);

          return _possibleConstructorReturn(this, (Icinga2ReportDatasource.__proto__ || Object.getPrototypeOf(Icinga2ReportDatasource)).call(this, instanceSettings, $q, backendSrv, templateSrv));
        }

        _createClass(Icinga2ReportDatasource, [{
          key: "mapToTextValue",
          value: function mapToTextValue(result) {
            return result.data;
          }
        }, {
          key: "buildQueryParameters",
          value: function buildQueryParameters(options) {
            //remove placeholder targets
            options.targets = _.filter(options.targets, target => {
              return target.target !== 'select metric';
            });
            var list_segments = options.targets[0].segments.slice(0)
            var query = createQuery(options.targets[0].target, list_segments)
            for (var i = 0; i < list_segments.length; i++){
              list_segments[i] = this.templateSrv.replace(list_segments[i], options.scopedVars)
              if (list_segments[i] == "(") {
                list_segments[i] = "#("
              }
              if (list_segments[i] == ")") {
                list_segments[i] = "#)"
              }
            }
            options.targets[0].query = query
            options.targets[0].segments = list_segments
            var targets = _.map(options.targets, target => {
              return {
                target: target.target,
                refId: target.refId,
                hide: target.hide,
                segments: target.segments,
                query: target.query
              };
            });

            options.targets = targets;
            return options;
          }
        }, {
          key: "getTasks",
          value: function getTasks(editor) {
            return this.doRequest({
              url: this.url + '/tasks'
            }).then(result => {
              return _.map(result.data.tasks, t => ({
                'text': t.name,
                'value': t.name
              }));
            });
          }
        }, {
          key: "updateExport",
          value: function updateExport(data) {
            return this.doRequest({
              url: this.url + '/tasks',
              method: 'POST',
              data: data
            });
          }
        }, {
          key: "getExportUrl",
          value: function getExportUrl(panel) {
            this.doRequest({
              method: 'POST',
              url: `${this.url}/query`,
              data: {
                dashboard: panel.dashboard.meta.slug,
                panel: panel.panel.id,
                targets: panel.panel.targets,
                timerange: panel.range.raw
              }
            });
            return `${this.url}/export?dashboard=${panel.dashboard.meta.slug}&panel=${panel.panel.id}`;
          }
        }]);

        return Icinga2ReportDatasource;
      }(BaseDatasource);

      _export("Datasource", Icinga2ReportDatasource);

      _export("QueryCtrl", Icinga2ReportQueryCtrl);

      _export("ConfigCtrl", BaseConfigCtrl);

      _export("QueryOptionsCtrl", BaseQueryOptionsCtrl);

      _export("AnnotationsQueryCtrl", BaseAnnotationsQueryCtrl);
    }
  };
});
//# sourceMappingURL=module.js.map


function createQuery(target, list_segments) {
  var dict_query = {}
  var SpecialSegment = ['WHERE', 'GROUP BY', 'Host Filter:', 'Service Filter:']
  var list_datasource = []
  var list_special_index = []
  list_datasource.push(target)
  count = 0
  // Find Datasource and find Special index
  for (var i = 0; i < list_segments.length; i++){
    if (SpecialSegment.includes(list_segments[i]) == true){
      count = count + 1
      list_special_index.push(i)
    }
    if (count == 0){
      list_datasource.push(list_segments[i])
    }
  }
  dict_query.datasource = list_datasource

  var list_condition_group = []
  // Group segment to Array base on Special index
  for (var i = 0; i < list_special_index.length; i ++) {
    var temp_array = []
    // Case 1: Last Group
    if (i ==  list_special_index.length - 1) {     // cuối
      for (var j = list_special_index[i]; j < list_segments.length ; j ++){
        if (list_segments[j] != "*") { 
          if (list_segments[j] == "(" || list_segments[j] == ")") { temp_array.push( "#" + list_segments[j]) }
          else { temp_array.push(list_segments[j]) }
        }
      }
      list_condition_group.push(temp_array)
    }
    // Case 2: Middle Group
    else{
      for (var j = list_special_index[i]; j < list_special_index[i + 1]; j ++){
        if (list_segments[j] != "*") { 
          if (list_segments[j] == "(" || list_segments[j] == ")") { temp_array.push( "#" + list_segments[j]) }
          else { temp_array.push(list_segments[j]) }
        }
      }
      list_condition_group.push(temp_array)
    }
  }

  var list_host_filter = []
  var list_dict_service_filter = []
  // Convert  to Dictonary
  for (var i = 0; i < list_condition_group.length; i ++) {
    // Case 1: Find Host Filter
    if (list_condition_group[i][0] == 'Host Filter:') {
      var temp_array = list_condition_group[i].splice(0)
      temp_array.shift()
      list_host_filter.push(temp_array.toString().replace(new RegExp(',','g'), ' '))
    }
    // Case 2: Find Service Filter
    else if (list_condition_group[i][0] == 'Service Filter:') {
      var dict_service_filter = {}
      var temp_array = list_condition_group[i].splice(0)
      temp_array.shift()
      index_filter = 0
      var filter = ""

      for (var j = 0; j < temp_array.length; j ++) {
        if (temp_array[j] == 'column_name') {
          dict_service_filter.column_name = temp_array[j + 2]
        }
        else if (temp_array[j] == 'state') {
          dict_service_filter.state = temp_array[j + 2]
          // index_filter = j + 2 + 2
        }
        else if (temp_array[j] == 'filter') {
          index_filter = j + 2
        }
        if (j >= index_filter && temp_array[j] != "*") {
          if (j == index_filter) {
            filter = temp_array[j]
          }
          else{
            filter = filter + " " + temp_array[j]
          }
        }
      }
      dict_service_filter.filter = filter
      list_dict_service_filter.push(dict_service_filter)
    }

    dict_query["hostFilter"] = list_host_filter
    dict_query["serviceFilter"] = list_dict_service_filter
  }
  // console.log(dict_query)
  return dict_query
}
