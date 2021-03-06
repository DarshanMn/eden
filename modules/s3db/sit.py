# -*- coding: utf-8 -*-

""" Sahana Eden Situation Model

    @copyright: 2009-2014 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ["S3SituationModel",
           "S3SituationReportModel",
           ]

from gluon import *
from gluon.storage import Storage
from ..s3 import *

# =============================================================================
class S3SituationModel(S3Model):
    """
        Situation Super Entity & Presence tables for Trackable resources
    """

    names = ["sit_situation",
             "sit_trackable",
             "sit_presence",
             "sit_location",
             ]

    def model(self):

        T = current.T

        location_id = self.gis_location_id

        configure = self.configure
        super_entity = self.super_entity

        # ---------------------------------------------------------------------
        # Situation Super-Entity
        #
        situation_types = Storage(irs_incident = T("Incident"),
                                  rms_req = T("Request"),
                                  pr_presence = T("Presence"),
                                  )

        tablename = "sit_situation"
        super_entity(tablename, "sit_id", situation_types,
                     Field("datetime", "datetime"),
                     location_id(),
                     )

        configure(tablename,
                  deletable = False,
                  editable = False,
                  listadd = False,
                  )

        # ---------------------------------------------------------------------
        # Trackable Types
        #
        # Use:
        #   - add a field with super_link("track_id", "sit_trackable")
        #   - add as super-entity in configure (super_entity=s3db.sit_trackable)
        #
        trackable_types = Storage(asset_asset = T("Asset"),
                                  dvi_body = T("Dead Body"),
                                  event_resource = T("Event Resource"),
                                  hrm_human_resource = T("Human Resource"),
                                  pr_person = T("Person"),
                                  )

        tablename = "sit_trackable"
        super_entity(tablename, "track_id",
                     trackable_types,
                     Field("track_timestmp", "datetime",
                           readable = False,
                           writable = False,
                           ),
                     )

        configure(tablename,
                  deletable = False,
                  editable = False,
                  listadd = False,
                  )

        # Components
        self.add_components(tablename,
                            # Presence
                            sit_presence=self.super_key("sit_trackable"),
                            )

        # ---------------------------------------------------------------------
        # Presence Records for trackables
        #
        # Use:
        #   - will be automatically available to all trackable types
        #
        tablename = "sit_presence"
        self.define_table(tablename,
                          self.super_link("track_id", "sit_trackable"),
                          Field("timestmp", "datetime",
                                label = T("Date/Time"),
                                ),
                          location_id(),
                          Field("interlock",
                                readable = False,
                                writable = False,
                                ),
                          *s3_meta_fields())

        # ---------------------------------------------------------------------
        # Pass names back to global scope (s3.*)
        #
        return dict(sit_location = self.sit_location,
                    )

    # ---------------------------------------------------------------------
    @staticmethod
    def sit_location(row, tablename):
        """
            Virtual Field to return the current location of a Trackable
            @ToDo: Bulk
            @ToDo: Also show Timestamp of when seen there
        """

        s3db = current.s3db
        tracker = S3Tracker()(s3db[tablename], row[tablename].id)
        location = tracker.get_location(as_rows=True).first()

        return s3db.gis_location_represent(None, row=location)

# =============================================================================
class S3SituationReportModel(S3Model):
    """
        Situation Reports
    """

    names = ["sit_report",
             ]

    def model(self):

        T = current.T

        # ---------------------------------------------------------------------
        # Situation Reports
        # - can be aggregated by OU
        #
        tablename = "sit_report"
        self.define_table(tablename,
                          self.super_link("doc_id", "doc_entity"),
                          Field("name", length=128,
                               label = T("Name"),
                               ),
                          self.org_organisation_id(),
                          self.gis_location_id(),
                          s3_date(),
                          s3_comments(),
                          *s3_meta_fields())

        # CRUD strings
        current.response.s3.crud_strings[tablename] = Storage(
                label_create = T("Add Situation Report"),
                title_display = T("Situation Report Details"),
                title_list = T("Situation Reports"),
                title_update = T("Edit Situation Report"),
                title_upload = T("Import Situation Reports"),
                label_list_button = T("List Situation Reports"),
                label_delete_button = T("Delete Situation Report"),
                msg_record_created = T("Situation Report added"),
                msg_record_modified = T("Situation Report updated"),
                msg_record_deleted = T("Situation Report deleted"),
                msg_list_empty = T("No Situation Reports currently registered"))

        # ---------------------------------------------------------------------
        # Pass names back to global scope (s3.*)
        #
        return dict()

# END =========================================================================
