// Runs inside an AVA (Moodle) tab: returns the signed-in student and every
// calendar event from tomorrow through the next school day, with full
// descriptions, links and attachments. The next school day is the first
// Monday–Friday after today that the AVA calendar does not mark as a holiday
// (feriado, recesso, sem aula, ponto facultativo); weekends and holidays in
// between are read too, so a sábado letivo or a notice still shows. Paste into
// javascript_tool as is. DAYS > 1 also reads that many school days.
const DAYS = 1; // quantos dias letivos olhar (1 = o próximo)
const HOLIDAY = /feriado|recesso|sem aula|ponto facultativo|f[ée]rias/i;
const call = async (methodname, args) => {
  const r = await fetch(`/lib/ajax/service.php?sesskey=${M.cfg.sesskey}&info=${methodname}`, {
    method: 'POST',
    body: JSON.stringify([{ index: 0, methodname, args }]),
  });
  const [res] = await r.json();
  if (res.error) throw new Error(`${methodname}: ${res.exception?.message}`);
  return res.data;
};
const text = (html) => {
  const d = new DOMParser().parseFromString(html || '', 'text/html');
  d.querySelectorAll('br,p,li,div,tr').forEach((n) => n.append('\n'));
  return d.body.textContent.replace(/[ \t ]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim();
};
const links = (html) =>
  [...new DOMParser().parseFromString(html || '', 'text/html').querySelectorAll('a[href]')]
    .map((a) => ({ text: a.textContent.trim(), href: a.href }));
const [user] = await call('core_user_get_users_by_field', { field: 'id', values: [String(M.cfg.userId)] });
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const days = [];
let school = 0;
for (let i = 1; school < DAYS && i <= 21; i++) {
  const d = new Date();
  d.setDate(d.getDate() + i);
  const view = await call('core_calendar_get_calendar_day_view', {
    year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate(),
  });
  const events = [];
  for (const e of view.events || []) {
    // An event shown in many old courses at once (e.g. a 6º ano notice copied to
    // every 2025 course) is kept once.
    if (events.some((x) => x.name === e.name && x.description === text(e.description))) continue;
    let files = [];
    if (e.modulename === 'assign' && e.instance) {
      try {
        const a = await call('mod_assign_get_assignments', { courseids: [e.course.id] });
        const asg = a.courses?.[0]?.assignments?.find((x) => x.id === e.instance);
        files = (asg?.introattachments || []).map((f) => ({ name: f.filename, url: f.fileurl }));
      } catch { /* the event's own text is enough */ }
    }
    events.push({
      date: iso(d),
      time: new Date(e.timestart * 1000).toTimeString().slice(0, 5),
      name: e.name,
      course: e.course?.fullname,
      kind: e.modulename || e.eventtype,
      url: e.url,
      description: text(e.description),
      links: links(e.description),
      files,
    });
  }
  const weekday = d.getDay() >= 1 && d.getDay() <= 5;
  const holiday = events.some((e) => HOLIDAY.test(e.name) && !/letivo/i.test(e.name));
  const kind = !weekday ? 'fim de semana' : holiday ? 'feriado' : 'dia letivo';
  if (kind === 'dia letivo') school++;
  days.push({ date: iso(d), weekday: d.toLocaleDateString('pt-BR', { weekday: 'long' }), kind, events });
}
({ student: user.fullname, userid: user.id, target: days.filter((x) => x.kind === 'dia letivo').map((x) => x.date), days });
