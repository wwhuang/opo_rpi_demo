drop table if exists interactions;
create table interactions (
  pid integer primary key autoincrement,
  rx_id integer not null,
  tx_id integer not null,
  range real not null,
  seq integer not null,
  time integer not null
);
