"""
Collection of views that are regenerated at the end of the migrate process. Currently
only postgres is supported.
"""
from typing import Dict


views: Dict[str, str] = {}

views['view_user'] = """create or replace view view_user as
select
  fu.id,
  cast(fu.payload->>'firstName' as varchar(255)) as first_name,
  cast(fu.payload->>'lastName' as varchar(255)) as last_name,
  cast(fu.payload->>'city' as varchar(255)) as city,
  to_date(cast(fu.payload->>'birthDate' as varchar(255)), 'dd.mm.yyyy') as birthdate
from
  fact_user fu;"""  # noqa

views['view_record_coopers'] = """create or replace view view_record_coopers as
select
  fr.id as record_id,
  fr.user_id,
  fr.event_id,
  coalesce(fe.event_at, fr.created_at) as created_at,
  cast(fr.payload->>'distance' as integer) as coopers,
  rank() over (partition by fr.user_id order by cast(fr.payload->>'distance' as integer) desc, coalesce(fe.event_at, fr.created_at) desc, fr.id) as rnk
from
  fact_record fr
left outer join
  fact_event fe on
    fr.event_id = fe.id
where
  fr.type_id = 1 -- Cooper's test
  and coalesce(fe.event_at, fr.created_at) >= now() - interval '2 years';"""  # noqa

views['view_record_pushups'] = """create or replace view view_record_pushups as
select
  fr.id as record_id,
  fr.user_id,
  fr.event_id,
  coalesce(fe.event_at, fr.created_at) as created_at,
  cast(fr.payload->>'pushups' as integer) as pushups,
  rank() over (partition by fr.user_id order by cast(fr.payload->>'pushups' as integer) desc, coalesce(fe.event_at, fr.created_at) desc, fr.id) as rnk
from
  fact_record fr
left outer join
  fact_event fe on
    fr.event_id = fe.id
where
  fr.type_id = 2 -- Push-up 60 sec
  and coalesce(fe.event_at, fr.created_at) >= now() - interval '2 years';"""  # noqa

views['view_record_situps'] = """create or replace view view_record_situps as
select
  fr.id as record_id,
  fr.user_id,
  fr.event_id,
  coalesce(fe.event_at, fr.created_at) as created_at,
  cast(fr.payload->>'situps' as integer) as situps,
  rank() over (partition by fr.user_id order by cast(fr.payload->>'situps' as integer) desc, coalesce(fe.event_at, fr.created_at) desc, fr.id) as rnk
from
  fact_record fr
left outer join
  fact_event fe on
    fr.event_id = fe.id
where
  fr.type_id = 3 -- situp 60 sec
  and coalesce(fe.event_at, fr.created_at) >= now() - interval '2 years';"""  # noqa

views['view_record_situps'] = """create or replace view view_record_situps as
select
  fr.id as record_id,
  fr.user_id,
  fr.event_id,
  coalesce(fe.event_at, fr.created_at) as created_at,
  cast(fr.payload->>'situps' as integer) as situps,
  rank() over (partition by fr.user_id order by cast(fr.payload->>'situps' as integer) desc, coalesce(fe.event_at, fr.created_at) desc, fr.id) as rnk
from
  fact_record fr
left outer join
  fact_event fe on
    fr.event_id = fe.id
where
  fr.type_id = 3 -- situp 60 sec
  and coalesce(fe.event_at, fr.created_at) >= now() - interval '2 years';"""  # noqa

views['view_record_standingjump'] = """create or replace view view_record_standingjump as
select
  fr.id as record_id,
  fr.user_id,
  fr.event_id,
  coalesce(fe.event_at, fr.created_at) as created_at,
  cast(fr.payload->>'standingjump' as integer) as standingjump,
  rank() over (partition by fr.user_id order by cast(fr.payload->>'standingjump' as integer) desc, coalesce(fe.event_at, fr.created_at) desc, fr.id) as rnk
from
  fact_record fr
left outer join
  fact_event fe on
    fr.event_id = fe.id
where
  fr.type_id = 4 -- standing jump test
  and coalesce(fe.event_at, fr.created_at) >= now() - interval '2 years';"""  # noqa

views['view_user_fa_index'] = """create or replace view view_user_fa_index as
select vu.first_name,
       vu.last_name,
       vu.city,
       vu.birthdate,
       vrc.coopers,
       vrp.pushups,
       vrs.situps,
       vrsj.standingjump,
       least(vrc.created_at, vrp.created_at, vrs.created_at, vrsj.created_at)::date as oldest_test_at,
       greatest(vrc.created_at, vrp.created_at, vrs.created_at, vrsj.created_at)::date as most_recent_test_at,
       age(greatest(vrc.created_at, vrp.created_at, vrs.created_at, vrsj.created_at)::date, vu.birthdate) as age_at_test,
       age(least(vrc.created_at, vrp.created_at, vrs.created_at, vrsj.created_at)::date, now()) + interval '2 years' as result_valid
from
     view_user vu
left outer join
  view_record_coopers vrc on vu.id = vrc.user_id
    and vrc.rnk = 1
left outer join
    view_record_pushups vrp on
        vu.id = vrp.user_id
        and vrp.rnk = 1
left outer join
    view_record_situps vrs on
        vu.id = vrs.user_id
        and vrs.rnk = 1
left outer join
    view_record_standingjump vrsj on
        vu.id = vrsj.user_id
        and vrsj.rnk = 1;"""  # noqa
