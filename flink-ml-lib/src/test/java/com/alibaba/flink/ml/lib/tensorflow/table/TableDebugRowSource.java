/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.alibaba.flink.ml.lib.tensorflow.table;

import com.alibaba.flink.ml.operator.util.TypeUtil;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.sources.StreamTableSource;
import org.apache.flink.types.Row;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;


public class TableDebugRowSource implements StreamTableSource<Row>, Serializable {

    private static Logger LOG = LoggerFactory.getLogger(TableDebugRowSource.class);
    private DebugRowSource debugRowSource;
    private TableSchema tableSchema;

    public TableDebugRowSource(TableSchema tableSchema) {
        this(0, tableSchema);
    }

    public TableDebugRowSource(int rank, TableSchema tableSchema) {
        this(rank, false, tableSchema);
    }
    public TableDebugRowSource(int rank, boolean hasString, TableSchema tableSchema) {
        this.debugRowSource = new DebugRowSource(rank, hasString, TypeUtil.schemaToRowTypeInfo(tableSchema));
        this.tableSchema = tableSchema;
    }



    @Override
    public TypeInformation<Row> getReturnType() {
        return TypeUtil.schemaToRowTypeInfo(tableSchema);
    }

    @Override
    public TableSchema getTableSchema() {
        return tableSchema;
    }

    @Override
    public String explainSource() {
        return "debug_source";
    }

    @Override
    public DataStream<Row> getDataStream(StreamExecutionEnvironment execEnv) {
        return execEnv.addSource(debugRowSource)
            .name(explainSource());
    }

}
