System.register(["lodash", "./app/plugins/panel/table/module", "./app/plugins/panel/table/editor", "./app/plugins/panel/table/column_options"], function (_export, _context) {
  "use strict";

  var _, TablePanelCtrl, tablePanelEditor, TablePanelEditorCtrl, columnOptionsTab;

  return {
    setters: [function (_lodash) {
      _ = _lodash.default;
    }, function (_appPluginsPanelTableModule) {
      TablePanelCtrl = _appPluginsPanelTableModule.TablePanelCtrl;
    }, function (_appPluginsPanelTableEditor) {
      tablePanelEditor = _appPluginsPanelTableEditor.tablePanelEditor;
      TablePanelEditorCtrl = _appPluginsPanelTableEditor.TablePanelEditorCtrl;
    }, function (_appPluginsPanelTableColumn_options) {
      columnOptionsTab = _appPluginsPanelTableColumn_options.columnOptionsTab;
    }],
    execute: function () {
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

      function _get(object, property, receiver) {
        if (object === null) object = Function.prototype;
        var desc = Object.getOwnPropertyDescriptor(object, property);

        if (desc === undefined) {
          var parent = Object.getPrototypeOf(object);

          if (parent === null) {
            return undefined;
          } else {
            return _get(parent, property, receiver);
          }
        } else if ("value" in desc) {
          return desc.value;
        } else {
          var getter = desc.get;

          if (getter === undefined) {
            return undefined;
          }

          return getter.call(receiver);
        }
      }

      function _classCallCheck(instance, Constructor) {
        if (!(instance instanceof Constructor)) {
          throw new TypeError("Cannot call a class as a function");
        }
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

      let EditorCtrl = function (_TablePanelEditorCtrl) {
        _inherits(EditorCtrl, _TablePanelEditorCtrl);

        function EditorCtrl($scope, $q, uiSegmentSrv) {
          _classCallCheck(this, EditorCtrl);

          return _possibleConstructorReturn(this, (EditorCtrl.__proto__ || Object.getPrototypeOf(EditorCtrl)).call(this, $scope, $q, uiSegmentSrv));
        }

        return EditorCtrl;
      }(TablePanelEditorCtrl);

      EditorCtrl.factory = function ($q, uiSegmentSrv) {
        return _.extend(tablePanelEditor($q, uiSegmentSrv), {
          controller: EditorCtrl,
          templateUrl: 'public/plugins/icinga2-report-panel/editor.html'
        });
      };

      let Icinga2ReportPanelCtrl = function (_TablePanelCtrl) {
        _inherits(Icinga2ReportPanelCtrl, _TablePanelCtrl);

        function Icinga2ReportPanelCtrl($scope, $injector, $rootScope) {
          var _this;

          _classCallCheck(this, Icinga2ReportPanelCtrl);

          _this = _possibleConstructorReturn(this, (Icinga2ReportPanelCtrl.__proto__ || Object.getPrototypeOf(Icinga2ReportPanelCtrl)).call(this, $scope, $injector));
          _this.$rootScope = $rootScope;
          _this.query = '';
          window.__panel = _this;
          return _this;
        }

        _createClass(Icinga2ReportPanelCtrl, [{
          key: "onInitEditMode",
          value: function onInitEditMode() {
            this.addEditorTab('Options', EditorCtrl.factory, 2);
            this.addEditorTab('Column Styles', columnOptionsTab, 3);
          }
        }, {
          key: "onDataReceived",
          value: function onDataReceived(dataList) {
            if (this.datasource.type === 'icinga2-report-datasource') {
              this.exportUrl = this.datasource.getExportUrl(this);
            }

            _get(Icinga2ReportPanelCtrl.prototype.__proto__ || Object.getPrototypeOf(Icinga2ReportPanelCtrl.prototype), "onDataReceived", this).call(this, dataList);
          }
        }, {
          key: "updateExport",
          value: function updateExport(editor) {
            this.datasource.updateExport({
              'task': editor.panel.exportTask,
              'interval': editor.panel.exportInterval,
              'targets': JSON.stringify(this.panel.targets)
            });
            editor.render();
          }
        }]);

        return Icinga2ReportPanelCtrl;
      }(TablePanelCtrl);

      Icinga2ReportPanelCtrl.panelDefaults = {
        targets: [{}],
        transform: 'timeseries_to_columns',
        pageSize: null,
        showHeader: true,
        styles: [{
          type: 'date',
          pattern: 'Time',
          alias: 'Time',
          dateFormat: 'YYYY-MM-DD HH:mm:ss'
        }, {
          unit: 'short',
          type: 'number',
          alias: '',
          decimals: 2,
          colors: ["rgba(245, 54, 54, 0.9)", "rgba(237, 129, 40, 0.89)", "rgba(50, 172, 45, 0.97)"],
          colorMode: null,
          pattern: '/.*/',
          thresholds: []
        }],
        columns: [],
        scroll: true,
        fontSize: '100%',
        sort: {
          col: 0,
          desc: true
        } // Icinga2ReportPanelCtrl.templateUrl = 'template.html'

      };

      _export("PanelCtrl", Icinga2ReportPanelCtrl);
    }
  };
});
//# sourceMappingURL=module.js.map
