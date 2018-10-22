DROP VIEW IF EXISTS agg_ccs_record_monthly CASCADE;
CREATE VIEW agg_ccs_record_monthly AS
    SELECT
        "awc_location_months"."awc_id" AS "awc_id",
        "awc_location_months"."awc_name" AS "awc_name",
        "awc_location_months"."awc_site_code" AS "awc_site_code",
        "awc_location_months"."supervisor_id" AS "supervisor_id",
        "awc_location_months"."supervisor_name" AS "supervisor_name",
        "awc_location_months"."supervisor_site_code" AS "supervisor_site_code",
        "awc_location_months"."block_id" AS "block_id",
        "awc_location_months"."block_name" AS "block_name",
        "awc_location_months"."block_site_code" AS "block_site_code",
        "awc_location_months"."district_id" AS "district_id",
        "awc_location_months"."district_name" AS "district_name",
        "awc_location_months"."district_site_code" AS "district_site_code",
        "awc_location_months"."state_id" AS "state_id",
        "awc_location_months"."state_name" AS "state_name",
        "awc_location_months"."state_site_code" AS "state_site_code",
        "awc_location_months"."aggregation_level" AS "aggregation_level",
        "awc_location_months"."block_map_location_name" AS "block_map_location_name",
        "awc_location_months"."district_map_location_name" AS "district_map_location_name",
        "awc_location_months"."state_map_location_name" AS "state_map_location_name",
        "awc_location_months"."month" AS "month",
        "awc_location_months"."contact_phone_number" AS "contact_phone_number",
        "awc_location_months"."aww_name" AS "aww_name",
        "agg_ccs_record"."ccs_status" AS "ccs_status",
        "agg_ccs_record"."trimester" AS "trimester",
        "agg_ccs_record"."caste" AS "caste",
        "agg_ccs_record"."disabled" AS "disabled",
        "agg_ccs_record"."minority" AS "minority",
        "agg_ccs_record"."resident" AS "resident",
        COALESCE("agg_ccs_record"."valid_in_month", 0) AS "valid_in_month",
        COALESCE("agg_ccs_record"."valid_all_registered_in_month", 0) AS "valid_all_registered_in_month",
        COALESCE("agg_ccs_record"."lactating", 0) AS "lactating",
        COALESCE("agg_ccs_record"."pregnant", 0) AS "pregnant",
        COALESCE("agg_ccs_record"."lactating_all", 0) AS "lactating_all",
        COALESCE("agg_ccs_record"."pregnant_all", 0) AS "pregnant_all",
        COALESCE("agg_ccs_record"."thr_eligible", 0) AS "thr_eligible",
        COALESCE("agg_ccs_record"."rations_21_plus_distributed", 0) AS "rations_21_plus_distributed",
        COALESCE("agg_ccs_record"."tetanus_complete", 0) AS "tetanus_complete",
        COALESCE("agg_ccs_record"."delivered_in_month", 0) AS "delivered_in_month",
        COALESCE("agg_ccs_record"."anc1_received_at_delivery", 0) AS "anc1_received_at_delivery",
        COALESCE("agg_ccs_record"."anc2_received_at_delivery", 0) AS "anc2_received_at_delivery",
        COALESCE("agg_ccs_record"."anc3_received_at_delivery", 0) AS "anc3_received_at_delivery",
        COALESCE("agg_ccs_record"."anc4_received_at_delivery", 0) AS "anc4_received_at_delivery",
        COALESCE("agg_ccs_record"."registration_trimester_at_delivery", 0) AS "registration_trimester_at_delivery",
        COALESCE("agg_ccs_record"."institutional_delivery_in_month", 0) AS "institutional_delivery_in_month",
        COALESCE("agg_ccs_record"."using_ifa", 0) AS "using_ifa",
        COALESCE("agg_ccs_record"."ifa_consumed_last_seven_days", 0) AS "ifa_consumed_last_seven_days",
        COALESCE("agg_ccs_record"."anemic_normal", 0) AS "anemic_normal",
        COALESCE("agg_ccs_record"."anemic_moderate", 0) AS "anemic_moderate",
        COALESCE("agg_ccs_record"."anemic_severe", 0) AS "anemic_severe",
        COALESCE("agg_ccs_record"."anemic_unknown", 0) AS "anemic_unknown",
        COALESCE("agg_ccs_record"."extra_meal", 0) AS "extra_meal",
        COALESCE("agg_ccs_record"."resting_during_pregnancy", 0) AS "resting_during_pregnancy",
        COALESCE("agg_ccs_record"."bp1_complete", 0) AS "bp1_complete",
        COALESCE("agg_ccs_record"."bp2_complete", 0) AS "bp2_complete",
        COALESCE("agg_ccs_record"."bp3_complete", 0) AS "bp3_complete",
        COALESCE("agg_ccs_record"."pnc_complete", 0) AS "pnc_complete",
        COALESCE("agg_ccs_record"."trimester_2", 0) AS "trimester_2",
        COALESCE("agg_ccs_record"."trimester_3", 0) AS "trimester_3",
        COALESCE("agg_ccs_record"."postnatal", 0) AS "postnatal",
        COALESCE("agg_ccs_record"."counsel_bp_vid", 0) AS "counsel_bp_vid",
        COALESCE("agg_ccs_record"."counsel_preparation", 0) AS "counsel_preparation",
        COALESCE("agg_ccs_record"."counsel_immediate_bf", 0) AS "counsel_immediate_bf",
        COALESCE("agg_ccs_record"."counsel_fp_vid", 0) AS "counsel_fp_vid",
        COALESCE("agg_ccs_record"."counsel_immediate_conception", 0) AS "counsel_immediate_conception",
        COALESCE("agg_ccs_record"."counsel_accessible_postpartum_fp", 0) AS "counsel_accessible_postpartum_fp",
        COALESCE("agg_ccs_record"."valid_visits", 0) AS "valid_visits",
        COALESCE("agg_ccs_record"."expected_visits", 0) AS "expected_vists"
    FROM "public"."awc_location_months" "awc_location_months"
    LEFT JOIN "public"."agg_ccs_record" "agg_ccs_record" ON (
        ("awc_location_months"."month" = "agg_ccs_record"."month") AND
        ("awc_location_months"."aggregation_level" = "agg_ccs_record"."aggregation_level") AND
        ("awc_location_months"."state_id" = "agg_ccs_record"."state_id") AND
        ("awc_location_months"."district_id" = "agg_ccs_record"."district_id") AND
        ("awc_location_months"."block_id" = "agg_ccs_record"."block_id") AND
        ("awc_location_months"."supervisor_id" = "agg_ccs_record"."supervisor_id") AND
        ("awc_location_months"."awc_id" = "agg_ccs_record"."awc_id")
    );
