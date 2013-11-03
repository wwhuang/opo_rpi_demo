drop table if exists interactions;
create table interactions (
  pid integer primary key autoincrement,
  rx_id integer not null,
  tx_id integer not null,
  range real not null,
  time integer not null,
  rtc_time integer not null,
  UNIQUE(rx_id, tx_id, rtc_time) ON CONFLICT REPLACE
);

drop table if exists id_map;
create table id_map (
	pid integer primary key autoincrement,
	ds2411_id integer not null,
	node_id integer not null
);