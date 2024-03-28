System.register(["lodash", "moment", "app/core/utils/kbn"], function (_export, _context) {
  "use strict";

  var _, moment, kbn;

  return {
    setters: [function (_lodash) {
      _ = _lodash.default;
    }, function (_moment) {
      moment = _moment.default;
    }, function (_appCoreUtilsKbn) {
      kbn = _appCoreUtilsKbn.default;
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

      let TableRenderer = function () {
        function TableRenderer(panel, table, isUtc, sanitize, templateSrv) {
          _classCallCheck(this, TableRenderer);

          Object.defineProperty(this, "formatters", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "colorState", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          this.panel = panel;
          this.table = table;
          this.initColumns();
        }

        _createClass(TableRenderer, [{
          key: "setTable",
          value: function setTable(table) {
            this.table = table;
            this.initColumns();
          }
        }, {
          key: "initColumns",
          value: function initColumns() {
            this.formatters = [];
            this.colorState = {};

            for (let colIndex = 0; colIndex < this.table.columns.length; colIndex++) {
              let column = this.table.columns[colIndex];
              column.title = column.text;

              for (let i = 0; i < this.panel.styles.length; i++) {
                let style = this.panel.styles[i];
                var regex = kbn.stringToJsRegex(style.pattern);

                if (column.text.match(regex)) {
                  column.style = style;

                  if (style.alias) {
                    column.title = column.text.replace(regex, style.alias);
                  }

                  break;
                }
              }

              this.formatters[colIndex] = this.createColumnFormatter(column);
            }
          }
        }, {
          key: "getColorForValue",
          value: function getColorForValue(value, style) {
            if (!style.thresholds) {
              return null;
            }

            for (var i = style.thresholds.length; i > 0; i--) {
              if (value >= style.thresholds[i - 1]) {
                return style.colors[i];
              }
            }

            return _.first(style.colors);
          }
        }, {
          key: "defaultCellFormatter",
          value: function defaultCellFormatter(v, style) {
            if (v === null || v === void 0 || v === undefined) {
              return '';
            }

            if (_.isArray(v)) {
              v = v.join(', ');
            }

            if (style && style.sanitize) {
              return this.sanitize(v);
            } else {
              return _.escape(v);
            }
          }
        }, {
          key: "createColumnFormatter",
          value: function createColumnFormatter(column) {
            if (!column.style) {
              return this.defaultCellFormatter;
            }

            if (column.style.type === 'hidden') {
              return v => {
                return undefined;
              };
            }

            if (column.style.type === 'date') {
              return v => {
                if (v === undefined || v === null) {
                  return '-';
                }

                if (_.isArray(v)) {
                  v = v[0];
                }

                var date = moment(v);

                if (this.isUtc) {
                  date = date.utc();
                }

                return date.format(column.style.dateFormat);
              };
            }
            // [Kien] - 24/04/2019 - Add the Mapping string feature - Start
            if (column.style.type === 'string') {
              return v => {
                if (_.isArray(v)) {
                  v = v.join(', ');
                }

                var mappingType = column.style.mappingType || 0;
                if (mappingType === 1 && column.style.valueMaps) {
                  for (let i = 0; i < column.style.valueMaps.length; i++) {
                    var map = column.style.valueMaps[i];
                    if (v === null) {
                      if (map.value === 'null') {
                        return map.text;
                      }
                      continue;
                    }

                    if ((!_.isString(v) && Number(map.value) === Number(v)) || map.value === v) {
                      this.setColorState(v, column.style);
                      return this.defaultCellFormatter(map.text, column.style);
                    }
                  }
                }

                if (mappingType === 2 && columns.style.rangeMaps) {
                  for (let i = 0; i < column.style.rangeMaps.length; i ++) {
                    var map = column.style.rangeMaps[i];

                    if (v === null) {
                      if (map.from === 'null' && map.to === 'null') {
                        return map.text;
                      }
                      continue;
                    }

                    if (Number(map.from) <= Number(v) && Number(map.to) >= Number(v)) {
                      this.setColorState(v, column.style);
                      return this.defaultCellFormatter(map.text, column.style);
                    }
                  }
                }

                if (v === null || v === void 0) {
                  return '-';
                }

                this.setColorState(v, column.style);
                return this.defaultCellFormatter(v, column.style);
              };
            }
            // [Kien] - 24/04/2019 - Add the Mapping string feature - End

            if (column.style.type === 'number') {
              let valueFormatter = kbn.valueFormats[column.unit || column.style.unit];
              return v => {
                if (v === null || v === void 0) {
                  return '-';
                }

                if (_.isString(v) || _.isArray(v)) {
                  return this.defaultCellFormatter(v, column.style);
                }

                if (column.style.colorMode) {
                  this.colorState[column.style.colorMode] = this.getColorForValue(v, column.style);
                }

                return valueFormatter(v, column.style.decimals, null);
              };
            }

            return value => {
              return this.defaultCellFormatter(value, column.style);
            };
          }
        }, {
          key: "setColorState",
          value: function setColorState(value, style) {
            if (!style.colorMode) {
              return;
            }

            if (value === null || value === void 0 || _.isArray(value)) {
              return;
            }
            var numericValue = Number(value);
            if (isNaN(numericValue)) {
              return;
            }
            this.colorState[style.colorMode] = this.getColorForValue(numericValue, style);
          }
        }, {
          key: "renderRowVariables",
          value: function renderRowVariables(rowIndex) {
            let scopedVars = {};
            let cell_variable;
            let row = this.table.rows[rowIndex];

            for (let i = 0; i < row.length; i++) {
              cell_variable = `__cell_${i}`;
              scopedVars[cell_variable] = {
                value: row[i]
              };
            }

            return scopedVars;
          }
        }, {
          key: "formatColumnValue",
          value: function formatColumnValue(colIndex, value) {
            return this.formatters[colIndex] ? this.formatters[colIndex](value) : value;
          }
        }, {
          key: "renderCell",
          value: function renderCell(columnIndex, rowIndex, value, addWidthHack = false) {
            value = this.formatColumnValue(columnIndex, value);
            var column = this.table.columns[columnIndex];
            var style = '';
            var cellClasses = [];
            var cellClass = '';

            if (this.colorState.cell) {
              style = ' style="background-color:' + this.colorState.cell + ';color: white"';
              this.colorState.cell = null;
            } else if (this.colorState.value) {
              style = ' style="color:' + this.colorState.value + '"';
              this.colorState.value = null;
            } // because of the fixed table headers css only solution
            // there is an issue if header cell is wider the cell
            // this hack adds header content to cell (not visible)


            var columnHtml = '';

            if (addWidthHack) {
              columnHtml = '<div class="table-panel-width-hack">' + this.table.columns[columnIndex].title + '</div>';
            }

            if (value === undefined) {
              style = ' style="display:none;"';
              column.hidden = true;
            } else {
              column.hidden = false;
            }

            if (column.style && column.style.preserveFormat) {
              cellClasses.push("table-panel-cell-pre");
            }

            if (column.style && column.style.link) {
              // Render cell as link
              var scopedVars = this.renderRowVariables(rowIndex);
              scopedVars['__cell'] = {
                value: value
              };
              var cellLink = this.templateSrv.replace(column.style.linkUrl, scopedVars);
              var cellLinkTooltip = this.templateSrv.replace(column.style.linkTooltip, scopedVars);
              var cellTarget = column.style.linkTargetBlank ? '_blank' : '';
              cellClasses.push("table-panel-cell-link");
              columnHtml += `
        <a href="${cellLink}" target="${cellTarget}" data-link-tooltip data-original-title="${cellLinkTooltip}" data-placement="right">
          ${value}
        </a>
      `;
            } else {
              columnHtml += value;
            }

            if (column.filterable) {
              cellClasses.push("table-panel-cell-filterable");
              columnHtml += `
        <a class="table-panel-filter-link" data-link-tooltip data-original-title="Filter out value" data-placement="bottom"
           data-row="${rowIndex}" data-column="${columnIndex}" data-operator="!=">
          <i class="fa fa-search-minus"></i>
        </a>
        <a class="table-panel-filter-link" data-link-tooltip data-original-title="Filter for value" data-placement="bottom"
           data-row="${rowIndex}" data-column="${columnIndex}" data-operator="=">
          <i class="fa fa-search-plus"></i>
        </a>`;
            }

            if (cellClasses.length) {
              cellClass = ' class="' + cellClasses.join(' ') + '"';
            }

            columnHtml = '<td' + cellClass + style + '>' + columnHtml + '</td>';
            return columnHtml;
          }
        }, {
          key: "render",
          value: function render(page) {
            let pageSize = this.panel.pageSize || 100;
            let startPos = page * pageSize;
            let endPos = Math.min(startPos + pageSize, this.table.rows.length);
            var html = "";

            for (var y = startPos; y < endPos; y++) {
              let row = this.table.rows[y];
              let cellHtml = '';
              let rowStyle = '';

              for (var i = 0; i < this.table.columns.length; i++) {
                cellHtml += this.renderCell(i, y, row[i], y === startPos);
              }

              if (this.colorState.row) {
                rowStyle = ' style="background-color:' + this.colorState.row + ';color: white"';
                this.colorState.row = null;
              }

              html += '<tr ' + rowStyle + '>' + cellHtml + '</tr>';
            }

            return html;
          }
        }, {
          key: "render_values",
          value: function render_values() {
            let rows = [];

            for (var y = 0; y < this.table.rows.length; y++) {
              let row = this.table.rows[y];
              let new_row = [];

              for (var i = 0; i < this.table.columns.length; i++) {
                new_row.push(this.formatColumnValue(i, row[i]));
              }

              rows.push(new_row);
            }

            return {
              columns: this.table.columns,
              rows: rows
            };
          }
        }]);

        return TableRenderer;
      }();

      _export("TableRenderer", TableRenderer);
    }
  };
});
//# sourceMappingURL=renderer.js.map
