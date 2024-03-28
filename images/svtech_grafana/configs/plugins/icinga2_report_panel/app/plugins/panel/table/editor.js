System.register(["lodash", "./transformers"], function (_export, _context) {
  "use strict";

  var _, transformers;

  return {
    setters: [function (_lodash) {
      _ = _lodash.default;
    }, function (_transformers) {
      transformers = _transformers.transformers;
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

      let TablePanelEditorCtrl = function () {
        /** @ngInject */
        function TablePanelEditorCtrl($scope, $q, uiSegmentSrv) {
          _classCallCheck(this, TablePanelEditorCtrl);

          Object.defineProperty(this, "panel", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "panelCtrl", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "transformers", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "fontSizes", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "addColumnSegment", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "getColumnNames", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "canSetColumns", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "columnsHelpMessage", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          $scope.editor = this;
          this.panelCtrl = $scope.ctrl;
          this.panel = this.panelCtrl.panel;
          this.transformers = transformers;
          this.fontSizes = ['80%', '90%', '100%', '110%', '120%', '130%', '150%', '160%', '180%', '200%', '220%', '250%'];
          this.addColumnSegment = uiSegmentSrv.newPlusButton();
          this.updateTransformHints();
        }

        _createClass(TablePanelEditorCtrl, [{
          key: "updateTransformHints",
          value: function updateTransformHints() {
            this.canSetColumns = false;
            this.columnsHelpMessage = '';

            switch (this.panel.transform) {
              case "timeseries_aggregations":
                {
                  this.canSetColumns = true;
                  break;
                }

              case "json":
                {
                  this.canSetColumns = true;
                  break;
                }

              case "table":
                {
                  this.columnsHelpMessage = "Columns and their order are determined by the data query";
                }
            }
          }
        }, {
          key: "getColumnOptions",
          value: function getColumnOptions() {
            if (!this.panelCtrl.dataRaw) {
              return this.$q.when([]);
            }

            var columns = this.transformers[this.panel.transform].getColumns(this.panelCtrl.dataRaw);

            var segments = _.map(columns, c => this.uiSegmentSrv.newSegment({
              value: c.text
            }));

            return this.$q.when(segments);
          }
        }, {
          key: "addColumn",
          value: function addColumn() {
            var columns = transformers[this.panel.transform].getColumns(this.panelCtrl.dataRaw);

            var column = _.find(columns, {
              text: this.addColumnSegment.value
            });

            if (column) {
              this.panel.columns.push(column);
              this.render();
            }

            var plusButton = this.uiSegmentSrv.newPlusButton();
            this.addColumnSegment.html = plusButton.html;
            this.addColumnSegment.value = plusButton.value;
          }
        }, {
          key: "transformChanged",
          value: function transformChanged() {
            this.panel.columns = [];

            if (this.panel.transform === 'timeseries_aggregations') {
              this.panel.columns.push({
                text: 'Avg',
                value: 'avg'
              });
            }

            this.updateTransformHints();
            this.render();
          }
        }, {
          key: "render",
          value: function render() {
            this.panelCtrl.render();
          }
        }, {
          key: "removeColumn",
          value: function removeColumn(column) {
            this.panel.columns = _.without(this.panel.columns, column);
            this.panelCtrl.render();
          }
        }]);

        return TablePanelEditorCtrl;
      }();

      _export("TablePanelEditorCtrl", TablePanelEditorCtrl);

      /** @ngInject */
      function tablePanelEditor($q, uiSegmentSrv) {
        'use strict';

        return {
          restrict: 'E',
          scope: true,
          templateUrl: 'public/app/plugins/panel/table/editor.html',
          controller: TablePanelEditorCtrl
        };
      }

      _export("tablePanelEditor", tablePanelEditor);
    }
  };
});
//# sourceMappingURL=editor.js.map
