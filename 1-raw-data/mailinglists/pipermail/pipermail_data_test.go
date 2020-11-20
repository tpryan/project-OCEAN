// Copyright 2020 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package pipermail

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/google/project-OCEAN/1-raw-data/utils"
)

func TestChangeMonthToDigit(t *testing.T) {

	tests := []struct {
		comparisonType string
		fileName       string
		wantName       string
	}{
		{
			comparisonType: "Test month string converted to two digit form",
			fileName:       "1851-October.txt.gz",
			wantName:       "1851-10.txt.gz",
		},
		{
			comparisonType: "Test month string converted to two digit form",
			fileName:       "3188-January.txt.gz",
			wantName:       "3188-01.txt.gz",
		},
	}

	for _, test := range tests {
		t.Run(test.comparisonType, func(t *testing.T) {
			gotName := changeMonthToDigit(test.fileName)
			if strings.Compare(test.wantName, gotName) != 0 {
				t.Errorf("Failed at converting month string to digits. Got: %v and wanted: %v.", gotName, test.wantName)
			}

		})

	}
}

func TestGetPipermailData(t *testing.T) {
	ctx := context.Background()
	storage := utils.NewFakeStorageConnection("pipermail")

	tests := []struct {
		comparisonType string
		gcs            *utils.FakeStorageConnection
		groupName      string
		httpToDom      utils.HttpDomResponse
		wantErr        error
	}{
		{
			comparisonType: "Test Storage called and no error",
			gcs:            storage,
			groupName:      "Pine-Leaf",
			httpToDom:      utils.FakeHttpDomResponse,
			wantErr:        nil,
		},
		{
			comparisonType: "Test Storage called and returns error",
			gcs:            storage,
			groupName:      "Missing",
			httpToDom:      utils.FakeHttpDomResponse,
			wantErr:        storageErr,
		},
	}

	for _, test := range tests {
		t.Run(test.comparisonType, func(t *testing.T) {
			if gotErr := GetPipermailData(ctx, test.gcs, test.groupName, test.httpToDom); !errors.Is(gotErr, test.wantErr) {
				if !strings.Contains(gotErr.Error(), test.wantErr.Error()) {
					t.Errorf("GetPipermailData response does not match.\n got: %v\nwant: %v", errors.Unwrap(gotErr), test.wantErr)
				}
			}
		})
	}
}
