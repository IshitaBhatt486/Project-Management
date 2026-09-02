import { createContext, type ButtonHTMLAttributes, type FormEvent, type ReactNode, useContext, useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import {
  Activity as ActivityIcon,
  ArrowDown,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  Clock3,
  FolderKanban,
  Layers3,
  LayoutDashboard,
  ListTodo,
  LogOut,
  Menu,
  Moon,
  MoreHorizontal,
  Pencil,
  Plus,
  RotateCcw,
  Search,
  Settings2,
  Sparkles,
  Sun,
  Target,
  Trash2,
  X,
  Zap,
} from 'lucide-react';
import {
  getGetDashboardSummaryQueryKey,
  getGetProjectQueryKey,
  getHealthCheckQueryKey,
  getListActivityQueryKey,
  getListProjectsQueryKey,
  getListTasksQueryKey,
  useCreateProject,
  useCreateTask,
  useDeleteTask,
  useGetDashboardSummary,
  useGetProject,
  useHealthCheck,
  useListActivity,
  useListProjects,
  useListTasks,
  useLogout,
  useUpdateProject,
  useUpdateTask,
  type Activity,
  type Project,
  type Task,
  type TaskPriority,
  type TaskStatus,
} from '@workspace/api-client-react';
import { AuthGate, useAuthUser } from '@/components/auth-gate';
import { AuthPage } from '@/components/auth-pages';
import { useQueryClient } from '@tanstack/react-query';
import {
  Route,
  Switch,
  useLocation,
  useParams,
  Router as WouterRouter,
} from 'wouter';

const queryClient = new QueryClient();

const statusLabels: Record<string, string> = { backlog: 'Backlog', todo: 'To do', in_progress: 'In progress', in_review: 'In review', done: 'Done' };
const priorityLabels: Record<string, string> = { low: 'Low', medium: 'Medium', high: 'High', urgent: 'Urgent' };
const statusColors: Record<string, string> = { backlog: 'slate', todo: 'blue', in_progress: 'amber', in_review: 'violet', done: 'teal' };
const projectColors = ['#d79b39', '#478477', '#c56b55', '#7389ae', '#aa7a9b'];

function cx(...parts: Array<string | false | null | undefined>) { return parts.filter(Boolean).join(' '); }
function formatDate(value?: string | null) {
  if (!value) return 'No due date';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(date);
}
function initials(name: string) { return name.split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase() || '—'; }
function isOverdue(value?: string | null) { return !!value && new Date(value).getTime() < Date.now(); }

type ThemeContextValue = { theme: 'light' | 'dark'; setTheme: (theme: 'light' | 'dark') => void };
const ThemeContext = createContext<ThemeContextValue>({ theme: 'light', setTheme: () => {} });
function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (localStorage.getItem('workbench-theme') as 'light' | 'dark') || 'light');
  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark'); localStorage.setItem('workbench-theme', theme); }, [theme]);
  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
}
function useTheme() {
  return useContext(ThemeContext);
}

function Button({ children, variant = 'secondary', className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'quiet' | 'danger' }) {
  return <button {...props} className={cx('btn', `btn-${variant}`, className)}>{children}</button>;
}
function Avatar({ name, small = false }: { name: string; small?: boolean }) { return <span className={cx('avatar', small && 'avatar-small')} data-testid={`avatar-${name}`}>{initials(name)}</span>; }
function StatusPill({ status }: { status: string }) { return <span className={cx('status-pill', `status-${statusColors[status] || 'slate'}`)}><span className="status-dot" />{statusLabels[status] || status}</span>; }
function PriorityPill({ priority }: { priority: string }) { return <span className={cx('priority-pill', `priority-${priority}`)}><span>{priority === 'urgent' ? '!' : priority === 'high' ? '↑' : priority === 'low' ? '↓' : '·'}</span>{priorityLabels[priority] || priority}</span>; }

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const [location] = useLocation();
  const user = useAuthUser();
  const items = [
    { href: '/', label: 'Overview', icon: LayoutDashboard },
    { href: '/projects', label: 'Projects', icon: FolderKanban },
    { href: '/tasks', label: 'Tasks', icon: ListTodo },
    { href: '/activity', label: 'Activity', icon: ActivityIcon },
  ];
  return <aside className="sidebar">
    <div className="brand"><span className="brand-mark"><Target size={17} /></span><span>workbench</span></div>
    <div className="workspace-switcher"><span className="workspace-avatar">N</span><span className="workspace-copy"><strong>Northstar</strong><small>Product studio</small></span><ChevronDown size={15} /></div>
    <p className="nav-label">Workspace</p>
    <nav className="nav-list">{items.map(({ href, label, icon: Icon }) => <a href={href} key={href} onClick={onNavigate} className={cx('nav-item', location === href && 'nav-item-active')} data-testid={`link-${label.toLowerCase()}`}><Icon size={17} /><span>{label}</span>{label === 'Tasks' && <span className="nav-count">12</span>}</a>)}</nav>
    <div className="sidebar-spacer" />
    <div className="sidebar-note"><Sparkles size={15} /><span>Small steps,<br />visible progress.</span></div>
    <a href="/settings" onClick={onNavigate} className={cx('nav-item', location === '/settings' && 'nav-item-active')} data-testid="link-settings"><Settings2 size={17} /><span>Settings</span></a>
     <div className="profile-row"><Avatar name={user?.name || 'Account'} small /><div><strong data-testid="text-sidebar-user-name">{user?.name || 'Account'}</strong><small data-testid="text-sidebar-user-email">{user?.email || 'Signed in'}</small></div><MoreHorizontal size={16} /></div>
  </aside>;
}

function ProfileMenu() {
  const user = useAuthUser();
  const logout = useLogout();
  const queryClient = useQueryClient();
  const [, setLocation] = useLocation();
  const [open, setOpen] = useState(false);
  const logoutError = logout.error instanceof Error ? logout.error.message : '';

  const signOut = () => {
    logout.mutate(undefined, {
      onSuccess: () => {
        queryClient.clear();
        setLocation('/login');
      },
    });
  };

  if (!user) return null;
  return (
    <div className="profile-menu">
      <button
        className="profile-trigger"
        onClick={() => setOpen((visible) => !visible)}
        aria-expanded={open}
        aria-haspopup="menu"
        data-testid="button-open-profile"
      >
        <Avatar name={user.name} small />
        <span className="profile-trigger-copy">
          <strong data-testid="text-current-user-name">{user.name}</strong>
          <small data-testid="text-current-user-email">{user.email}</small>
        </span>
        <ChevronDown size={14} className={cx('profile-chevron', open && 'profile-chevron-open')} />
      </button>
      {open && (
        <div className="profile-dropdown" role="menu" data-testid="menu-profile">
          <div className="profile-dropdown-heading">
            <span className="profile-dropdown-label">Signed in as</span>
            <strong>{user.name}</strong>
            <small>{user.email}</small>
          </div>
          {logoutError && <p className="profile-error" role="alert" data-testid="auth-state-logout-error">{logoutError}</p>}
          <button className="profile-logout" onClick={signOut} disabled={logout.isPending} role="menuitem" data-testid="button-logout">
            <LogOut size={15} />
            <span>{logout.isPending ? 'Signing out…' : 'Sign out'}</span>
          </button>
        </div>
      )}
    </div>
  );
}

function Topbar({ onMenu }: { onMenu: () => void }) {
  const { theme, setTheme } = useTheme();
  const [location] = useLocation();
  const pageTitle = location === '/' ? 'Overview' : location.slice(1).split('/')[0].replace('-', ' ');
  return <header className="topbar">
    <button className="mobile-menu" onClick={onMenu} data-testid="button-open-menu"><Menu size={20} /></button>
    <div className="breadcrumb"><span>Northstar</span><span className="breadcrumb-slash">/</span><strong>{pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1)}</strong></div>
    <div className="topbar-actions">
      <button className="icon-btn search-trigger" data-testid="button-search" aria-label="Search"><Search size={18} /><span>Search</span><kbd>⌘ K</kbd></button>
      <button className="icon-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} data-testid="button-toggle-theme" aria-label="Toggle theme">{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
       <ProfileMenu />
    </div>
  </header>;
}

function Shell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  return <div className="app-noise app-shell"><div className={cx('mobile-overlay', mobileOpen && 'mobile-overlay-visible')} onClick={() => setMobileOpen(false)} /><div className={cx('sidebar-wrap', mobileOpen && 'sidebar-wrap-open')}><Sidebar onNavigate={() => setMobileOpen(false)} /></div><div className="main-shell"><Topbar onMenu={() => setMobileOpen(true)} /><main className="main-content page-enter">{children}</main></div></div>;
}

function LoadingState({ label = 'Loading your workspace' }: { label?: string }) { return <div className="loading-state"><div className="skeleton loading-line" /><div className="skeleton loading-line short" /><span>{label}</span></div>; }
function ErrorState({ onRetry, label = 'The workspace could not be reached.' }: { onRetry?: () => void; label?: string }) { return <div className="empty-state"><CircleAlert size={28} /><h3>Something got in the way</h3><p>{label}</p>{onRetry && <Button onClick={onRetry}><RotateCcw size={15} />Try again</Button>}</div>; }
function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) { return <div className="empty-state"><div className="empty-icon"><Layers3 size={22} /></div><h3>{title}</h3><p>{description}</p>{action}</div>; }

function StatCard({ label, value, detail, accent, icon: Icon }: { label: string; value: number | string; detail: string; accent: string; icon: typeof Target }) {
  return <div className="stat-card"><div className={cx('stat-icon', `stat-${accent}`)}><Icon size={18} /></div><div><p>{label}</p><strong data-testid={`stat-${label.toLowerCase().replaceAll(' ', '-')}`}>{value}</strong><small>{detail}</small></div></div>;
}

function TaskRow({ task, onEdit, onDelete, onStatus }: { task: Task; onEdit?: (task: Task) => void; onDelete?: (task: Task) => void; onStatus?: (task: Task, status: TaskStatus) => void }) {
  return <div className="task-row" data-testid={`row-task-${task.id}`}>
    <button className={cx('task-check', task.status === 'done' && 'task-check-done')} onClick={() => onStatus?.(task, task.status === 'done' ? 'todo' : 'done')} data-testid={`button-complete-task-${task.id}`} aria-label={`Mark ${task.title} ${task.status === 'done' ? 'open' : 'complete'}`}>{task.status === 'done' && <Check size={13} />}</button>
    <div className="task-main"><strong className={task.status === 'done' ? 'task-done' : ''}>{task.title}</strong><span>{task.description || 'No description'}</span></div>
    <StatusPill status={task.status} /><PriorityPill priority={task.priority} />
    <div className="task-assignee">{task.assignee ? <><Avatar name={task.assignee} small /><span>{task.assignee}</span></> : <span className="muted">Unassigned</span>}</div>
    <span className={cx('task-due', isOverdue(task.dueDate) && task.status !== 'done' && 'due-overdue')}>{formatDate(task.dueDate)}</span>
    {onEdit && <button className="row-action" onClick={() => onEdit(task)} data-testid={`button-edit-task-${task.id}`} aria-label={`Edit ${task.title}`}><Pencil size={15} /></button>}
    {onDelete && <button className="row-action row-delete" onClick={() => onDelete(task)} data-testid={`button-delete-task-${task.id}`} aria-label={`Delete ${task.title}`}><Trash2 size={15} /></button>}
  </div>;
}

function ProgressRing({ value, label }: { value: number; label: string }) { const radius = 32; const circumference = 2 * Math.PI * radius; return <div className="progress-ring"><svg width="84" height="84" viewBox="0 0 84 84"><circle className="ring-track" cx="42" cy="42" r={radius} /><circle className="ring-value" cx="42" cy="42" r={radius} strokeDasharray={circumference} strokeDashoffset={circumference - (value / 100) * circumference} /></svg><div><strong>{value}%</strong><span>{label}</span></div></div>; }

function Overview() {
  const user = useAuthUser();
  const summaryQuery = useGetDashboardSummary();
  const projectsQuery = useListProjects();
  const tasksQuery = useListTasks();
  const activityQuery = useListActivity();
  useHealthCheck({ query: { staleTime: 30000, queryKey: getHealthCheckQueryKey() } });
  const summary = summaryQuery.data;
  const projects = projectsQuery.data || [];
  const tasks = tasksQuery.data || [];
  const recentTasks = tasks.slice().sort((a, b) => Number(a.status === 'done') - Number(b.status === 'done')).slice(0, 5);
  const completion = summary && summary.openTaskCount + summary.completedTaskCount > 0 ? Math.round((summary.completedTaskCount / (summary.openTaskCount + summary.completedTaskCount)) * 100) : 0;
  if (summaryQuery.isLoading || projectsQuery.isLoading || tasksQuery.isLoading) return <LoadingState />;
  if (summaryQuery.isError || projectsQuery.isError || tasksQuery.isError) return <ErrorState onRetry={() => { summaryQuery.refetch(); projectsQuery.refetch(); tasksQuery.refetch(); }} />;
  return <div className="content-stack">
     <div className="page-heading"><div><p className="eyebrow">Tuesday, October 15, 2024</p><h1>Good morning, {user?.name.split(' ')[0] || 'there'}<span className="heading-period">.</span></h1><p className="page-subtitle">Here’s the shape of your work today.</p></div><a href="/tasks" className="btn btn-primary" data-testid="link-add-task-overview"><Plus size={16} />New task</a></div>
    <section className="stat-grid">
      <StatCard label="Projects" value={summary?.projectCount ?? projects.length} detail="active workspaces" accent="gold" icon={FolderKanban} />
      <StatCard label="Open tasks" value={summary?.openTaskCount ?? 0} detail="across all projects" accent="teal" icon={ListTodo} />
      <StatCard label="In progress" value={summary?.inProgressTaskCount ?? 0} detail="moving right now" accent="blue" icon={Zap} />
      <StatCard label="Overdue" value={summary?.overdueTaskCount ?? 0} detail="needs a closer look" accent="coral" icon={Clock3} />
    </section>
    <div className="overview-grid">
      <section className="panel current-work"><div className="panel-header"><div><p className="eyebrow">Current work</p><h2>Keep the thread moving</h2></div><a href="/tasks" className="text-link" data-testid="link-view-all-tasks">View all <ArrowUpRight size={14} /></a></div>
        {recentTasks.length ? <div className="task-list">{recentTasks.map((task) => <TaskRow key={task.id} task={task} />)}</div> : <EmptyState title="A clear bench" description="Create a task when the next piece of work takes shape." action={<a className="btn btn-primary" href="/tasks" data-testid="link-create-first-task"><Plus size={15} />Create a task</a>} />}
      </section>
      <section className="panel progress-panel"><div className="panel-header"><div><p className="eyebrow">Workspace pulse</p><h2>Progress, at a glance</h2></div><MoreHorizontal size={18} className="muted" /></div><div className="progress-wrap"><ProgressRing value={completion} label="complete" /><div className="progress-copy"><strong>{summary?.completedTaskCount ?? 0} tasks finished</strong><p>Small, deliberate progress adds up. Keep the good rhythm.</p></div></div><div className="mini-metrics"><div><span className="metric-bar bar-teal" /><strong>{summary?.completedTaskCount ?? 0}</strong><small>completed</small></div><div><span className="metric-bar bar-amber" /><strong>{summary?.inProgressTaskCount ?? 0}</strong><small>in motion</small></div><div><span className="metric-bar bar-coral" /><strong>{summary?.overdueTaskCount ?? 0}</strong><small>overdue</small></div></div></section>
    </div>
    <div className="lower-grid">
      <section className="panel projects-preview"><div className="panel-header"><div><p className="eyebrow">Your projects</p><h2>Rooms for the work</h2></div><a href="/projects" className="text-link" data-testid="link-view-projects">All projects <ArrowUpRight size={14} /></a></div>{projects.length ? <div className="project-mini-list">{projects.slice(0, 4).map((project) => <a href={`/projects/${project.id}`} className="project-mini" key={project.id} data-testid={`link-project-${project.id}`}><span className="project-color" style={{ backgroundColor: project.color || projectColors[project.id % projectColors.length] }} /><span><strong>{project.name}</strong><small><span className="font-mono-app">{project.key}</span> · {project.taskCount} tasks</small></span><span className="project-percent">{project.taskCount ? Math.round(project.completedTaskCount / project.taskCount * 100) : 0}%</span></a>)}</div> : <EmptyState title="No projects yet" description="Start with one focused space for the work." action={<a href="/projects" className="btn btn-secondary" data-testid="link-create-project-empty"><Plus size={15} />New project</a>} />}</section>
      <ActivityFeed activities={(activityQuery.data || []).slice(0, 4)} loading={activityQuery.isLoading} />
    </div>
  </div>;
}

function ActivityFeed({ activities, loading }: { activities: Activity[]; loading?: boolean }) {
  return <section className="panel activity-panel"><div className="panel-header"><div><p className="eyebrow">Latest signals</p><h2>Recent activity</h2></div><a href="/activity" className="text-link" data-testid="link-view-activity">See all <ArrowUpRight size={14} /></a></div>{loading ? <div className="activity-skeleton"><div className="skeleton" /><div className="skeleton" /><div className="skeleton" /></div> : activities.length ? <div className="activity-list">{activities.map((item) => <ActivityItem key={item.id} activity={item} />)}</div> : <EmptyState title="The room is quiet" description="Updates from your team will gather here." />}</section>;
}
function ActivityItem({ activity }: { activity: Activity }) {
  const icon = activity.kind === 'task_completed' ? <CheckCircle2 size={16} /> : activity.kind === 'project_created' ? <FolderKanban size={16} /> : activity.kind === 'task_created' ? <Plus size={16} /> : <Pencil size={16} />;
  return <div className="activity-item" data-testid={`activity-${activity.id}`}><span className={cx('activity-icon', activity.kind === 'task_completed' && 'activity-done')}>{icon}</span><div><strong>{activity.message}</strong><small>{activity.projectName} <span>·</span> {formatRelative(activity.createdAt)}</small></div></div>;
}
function formatRelative(value: string) { const then = new Date(value).getTime(); if (Number.isNaN(then)) return value; const mins = Math.floor((Date.now() - then) / 60000); if (mins < 60) return `${Math.max(mins, 1)}m ago`; const hrs = Math.floor(mins / 60); if (hrs < 24) return `${hrs}h ago`; return `${Math.floor(hrs / 24)}d ago`; }

function ProjectsPage() {
  const query = useListProjects();
  const client = useQueryClient();
  const create = useCreateProject();
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', key: '', description: '', color: projectColors[0] });
  const projects = (query.data || []).filter((p) => `${p.name} ${p.key}`.toLowerCase().includes(search.toLowerCase()));
  const submit = (event: FormEvent) => { event.preventDefault(); if (!form.name.trim() || !form.key.trim()) return; create.mutate({ data: form }, { onSuccess: () => { setShowCreate(false); setForm({ name: '', key: '', description: '', color: projectColors[0] }); client.invalidateQueries({ queryKey: getListProjectsQueryKey() }); } }); };
  return <div className="content-stack"><div className="page-heading"><div><p className="eyebrow">Workspace / Projects</p><h1>Projects<span className="heading-period">.</span></h1><p className="page-subtitle">A small number of clear rooms beats a crowded hallway.</p></div><Button variant="primary" onClick={() => setShowCreate(true)} data-testid="button-new-project"><Plus size={16} />New project</Button></div>
    <div className="toolbar"><div className="search-field"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Find a project" data-testid="input-search-projects" /></div><span className="toolbar-count">{projects.length} project{projects.length === 1 ? '' : 's'}</span></div>
    {query.isLoading ? <LoadingState label="Arranging projects" /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : projects.length ? <div className="project-grid">{projects.map((project) => <ProjectCard key={project.id} project={project} />)}</div> : <EmptyState title={search ? 'Nothing matches that search' : 'Make room for the first project'} description={search ? 'Try a different name or key.' : 'Projects give tasks a place to belong and a direction to follow.'} action={!search && <Button variant="primary" onClick={() => setShowCreate(true)} data-testid="button-create-empty-project"><Plus size={15} />Create project</Button>} />}
    {showCreate && <ProjectModal form={form} setForm={setForm} onClose={() => setShowCreate(false)} onSubmit={submit} pending={create.isPending} />}
  </div>;
}
function ProjectCard({ project }: { project: Project }) { const percent = project.taskCount ? Math.round(project.completedTaskCount / project.taskCount * 100) : 0; return <a className="project-card" href={`/projects/${project.id}`} data-testid={`card-project-${project.id}`}><div className="project-card-top"><span className="project-color large" style={{ backgroundColor: project.color || projectColors[project.id % projectColors.length] }} /><span className="font-mono-app project-key">{project.key}</span><ArrowUpRight size={17} className="card-arrow" /></div><h2>{project.name}</h2><p>{project.description || 'A focused space for good work.'}</p><div className="project-card-bottom"><div className="progress-track"><span style={{ width: `${percent}%`, backgroundColor: project.color || 'hsl(var(--primary))' }} /></div><span>{percent}% <small>complete</small></span></div><div className="project-card-meta"><span>{project.taskCount} tasks</span><span>{project.completedTaskCount} done</span></div></a>; }
function ProjectModal({ form, setForm, onClose, onSubmit, pending }: { form: { name: string; key: string; description: string; color: string }; setForm: (form: { name: string; key: string; description: string; color: string }) => void; onClose: () => void; onSubmit: (e: FormEvent) => void; pending: boolean }) { return <Modal title="New project" onClose={onClose}><form onSubmit={onSubmit} className="form-stack"><label>Project name<input autoFocus value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Mobile checkout" data-testid="input-project-name" /></label><label>Short key<input maxLength={6} value={form.key} onChange={(e) => setForm({ ...form, key: e.target.value.toUpperCase() })} placeholder="e.g. MC" data-testid="input-project-key" /></label><label>What is this for?<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="A sentence that keeps the room oriented." data-testid="input-project-description" /></label><fieldset><legend>Color marker</legend><div className="color-options">{projectColors.map((color) => <button type="button" key={color} className={cx('color-option', form.color === color && 'color-option-selected')} style={{ background: color }} onClick={() => setForm({ ...form, color })} data-testid={`button-color-${color.slice(1)}`} aria-label={`Use ${color}`} />)}</div></fieldset><div className="modal-actions"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" disabled={pending}>{pending ? 'Creating…' : 'Create project'}</Button></div></form></Modal>; }

function TasksPage() {
  const [statusFilter, setStatusFilter] = useState<'all' | TaskStatus>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | TaskPriority>('all');
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [deleting, setDeleting] = useState<Task | null>(null);
  const client = useQueryClient();
  const projectsQuery = useListProjects();
  const query = useListTasks(statusFilter === 'all' ? undefined : { status: statusFilter });
  const create = useCreateTask(); const update = useUpdateTask(); const remove = useDeleteTask();
  const tasks = (query.data || []).filter((task) => priorityFilter === 'all' || task.priority === priorityFilter);
  const saveTask = (data: Record<string, unknown>) => { if (editing) update.mutate({ taskId: editing.id, data: data as never }, { onSuccess: () => { setEditing(null); invalidateTaskData(client); } }); else create.mutate({ data: data as never }, { onSuccess: () => { setShowCreate(false); invalidateTaskData(client); } }); };
  const changeStatus = (task: Task, status: TaskStatus) => update.mutate({ taskId: task.id, data: { status } }, { onSuccess: () => invalidateTaskData(client) });
  const deleteTask = () => { if (!deleting) return; remove.mutate({ taskId: deleting.id }, { onSuccess: () => { setDeleting(null); invalidateTaskData(client); } }); };
  return <div className="content-stack"><div className="page-heading"><div><p className="eyebrow">Workspace / Tasks</p><h1>Tasks<span className="heading-period">.</span></h1><p className="page-subtitle">The next useful thing, made visible.</p></div><Button variant="primary" onClick={() => setShowCreate(true)} data-testid="button-new-task"><Plus size={16} />New task</Button></div>
    <div className="filter-toolbar"><div className="filter-group"><span className="filter-label">Status</span>{(['all', 'backlog', 'todo', 'in_progress', 'in_review', 'done'] as const).map((status) => <button key={status} className={cx('filter-chip', statusFilter === status && 'filter-chip-active')} onClick={() => setStatusFilter(status)} data-testid={`button-filter-${status}`}>{status === 'all' ? 'All' : statusLabels[status]}</button>)}</div><label className="select-wrap"><span>Priority</span><select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value as 'all' | TaskPriority)} data-testid="select-filter-priority"><option value="all">All priorities</option>{Object.entries(priorityLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select><ChevronDown size={14} /></label></div>
    {query.isLoading ? <LoadingState label="Gathering your tasks" /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : tasks.length ? <section className="panel task-table"><div className="task-table-head"><span>Task</span><span>Status</span><span>Priority</span><span>Owner</span><span>Due</span><span /></div>{tasks.map((task) => <TaskRow key={task.id} task={task} onEdit={setEditing} onDelete={setDeleting} onStatus={changeStatus} />)}</section> : <EmptyState title="A clean slate" description="There are no tasks in this view. Add the next step to get moving." action={<Button variant="primary" onClick={() => setShowCreate(true)} data-testid="button-create-empty-task"><Plus size={15} />Create a task</Button>} />}
    {(showCreate || editing) && <TaskModal task={editing} projects={projectsQuery.data || []} onClose={() => { setShowCreate(false); setEditing(null); }} onSave={saveTask} pending={create.isPending || update.isPending} />}
    {deleting && <ConfirmModal title="Delete this task?" description={`“${deleting.title}” will be removed from the workspace.`} onClose={() => setDeleting(null)} onConfirm={deleteTask} pending={remove.isPending} />}
  </div>;
}
function invalidateTaskData(client: ReturnType<typeof useQueryClient>) { client.invalidateQueries({ queryKey: getListTasksQueryKey() }); client.invalidateQueries({ queryKey: getGetDashboardSummaryQueryKey() }); client.invalidateQueries({ queryKey: getListActivityQueryKey() }); }
function TaskModal({ task, projects, onClose, onSave, pending }: { task: Task | null; projects: Project[]; onClose: () => void; onSave: (data: Record<string, unknown>) => void; pending: boolean }) {
  const [form, setForm] = useState({ projectId: task?.projectId || projects[0]?.id || 0, title: task?.title || '', description: task?.description || '', status: task?.status || 'todo', priority: task?.priority || 'medium', assignee: task?.assignee || '', dueDate: task?.dueDate?.slice(0, 10) || '' });
  return <Modal title={task ? 'Edit task' : 'New task'} onClose={onClose}><form className="form-stack" onSubmit={(e) => { e.preventDefault(); if (!form.title.trim() || (!task && !form.projectId)) return; onSave({ ...form, projectId: Number(form.projectId), dueDate: form.dueDate || null }); }}><label>Task title<input autoFocus value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="What needs to happen?" data-testid="input-task-title" /></label><label>Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Add enough context for the next person." data-testid="input-task-description" /></label>{!task && <label>Project<select value={form.projectId} onChange={(e) => setForm({ ...form, projectId: Number(e.target.value) })} data-testid="select-task-project">{projects.length ? projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>) : <option value={0}>Choose a project first</option>}</select></label>}<div className="form-two"><label>Status<select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as TaskStatus })} data-testid="select-task-status">{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label>Priority<select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value as TaskPriority })} data-testid="select-task-priority">{Object.entries(priorityLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label></div><div className="form-two"><label>Assignee<input value={form.assignee} onChange={(e) => setForm({ ...form, assignee: e.target.value })} placeholder="Name" data-testid="input-task-assignee" /></label><label>Due date<input type="date" value={form.dueDate} onChange={(e) => setForm({ ...form, dueDate: e.target.value })} data-testid="input-task-due-date" /></label></div><div className="modal-actions"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" disabled={pending}>{pending ? 'Saving…' : task ? 'Save changes' : 'Create task'}</Button></div></form></Modal>;
}

function ProjectDetailPage() {
  const params = useParams<{ id: string }>(); const id = Number(params.id); const client = useQueryClient();
  const projectQuery = useGetProject(id, { query: { enabled: Number.isFinite(id), queryKey: getGetProjectQueryKey(id) } });
  const tasksQuery = useListTasks({ projectId: id }); const update = useUpdateProject(); const updateTask = useUpdateTask();
  const [editing, setEditing] = useState(false); const [showTask, setShowTask] = useState(false); const [editingTask, setEditingTask] = useState<Task | null>(null);
  const createTask = useCreateTask();
  const project = projectQuery.data; const tasks = tasksQuery.data || [];
  if (projectQuery.isLoading) return <LoadingState label="Opening project" />; if (projectQuery.isError || !project) return <ErrorState label="This project could not be found." onRetry={() => projectQuery.refetch()} />;
  const percent = project.taskCount ? Math.round(project.completedTaskCount / project.taskCount * 100) : 0;
  return <div className="content-stack"><a href="/projects" className="back-link" data-testid="link-back-projects"><ArrowDown size={15} />Back to projects</a><div className="project-detail-heading"><div className="project-title-mark" style={{ backgroundColor: project.color }} /><div><p className="eyebrow font-mono-app">{project.key}</p><h1>{project.name}<span className="heading-period">.</span></h1><p className="page-subtitle">{project.description || 'A focused space for good work.'}</p></div><div className="heading-actions"><Button onClick={() => setEditing(true)} data-testid="button-edit-project"><Pencil size={15} />Edit project</Button><Button variant="primary" onClick={() => setShowTask(true)} data-testid="button-add-project-task"><Plus size={15} />Add task</Button></div></div><div className="detail-stats"><div><span>Progress</span><strong>{percent}%</strong></div><div><span>All tasks</span><strong>{project.taskCount}</strong></div><div><span>Completed</span><strong>{project.completedTaskCount}</strong></div><div><span>Open</span><strong>{Math.max(project.taskCount - project.completedTaskCount, 0)}</strong></div></div><section className="panel task-table"><div className="panel-header"><div><p className="eyebrow">Project tasks</p><h2>The work in this room</h2></div><span className="toolbar-count">{tasks.length} total</span></div>{tasksQuery.isLoading ? <LoadingState /> : tasks.length ? <div>{tasks.map((task) => <TaskRow key={task.id} task={task} onEdit={setEditingTask} onStatus={(item, status) => updateTask.mutate({ taskId: item.id, data: { status } }, { onSuccess: () => { client.invalidateQueries({ queryKey: getGetProjectQueryKey(id) }); client.invalidateQueries({ queryKey: getListTasksQueryKey({ projectId: id }) }); } })} />)}</div> : <EmptyState title="No tasks in this room" description="Add the first step and give the project somewhere to go." action={<Button variant="primary" onClick={() => setShowTask(true)} data-testid="button-create-project-task-empty"><Plus size={15} />Add task</Button>} />}</section>{editing && <ProjectEditModal project={project} onClose={() => setEditing(false)} onSave={(data) => update.mutate({ projectId: id, data }, { onSuccess: () => { setEditing(false); client.invalidateQueries({ queryKey: getGetProjectQueryKey(id) }); client.invalidateQueries({ queryKey: getListProjectsQueryKey() }); } })} pending={update.isPending} />}{(showTask || editingTask) && <TaskModal task={editingTask} projects={[project]} onClose={() => { setShowTask(false); setEditingTask(null); }} onSave={(data) => editingTask ? updateTask.mutate({ taskId: editingTask.id, data: data as never }, { onSuccess: () => { client.invalidateQueries({ queryKey: getGetProjectQueryKey(id) }); client.invalidateQueries({ queryKey: getListTasksQueryKey({ projectId: id }) }); setEditingTask(null); } }) : createTask.mutate({ data: data as never }, { onSuccess: () => { client.invalidateQueries({ queryKey: getGetProjectQueryKey(id) }); client.invalidateQueries({ queryKey: getListTasksQueryKey({ projectId: id }) }); setShowTask(false); } })} pending={createTask.isPending || updateTask.isPending} />}</div>;
}
function ProjectEditModal({ project, onClose, onSave, pending }: { project: Project; onClose: () => void; onSave: (data: { name: string; description: string; color: string }) => void; pending: boolean }) { const [form, setForm] = useState({ name: project.name, description: project.description, color: project.color }); return <Modal title="Edit project" onClose={onClose}><form className="form-stack" onSubmit={(e) => { e.preventDefault(); onSave(form); }}><label>Project name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="input-edit-project-name" /></label><label>Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} data-testid="input-edit-project-description" /></label><div className="modal-actions"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" disabled={pending}>{pending ? 'Saving…' : 'Save changes'}</Button></div></form></Modal>; }

function ActivityPage() { const query = useListActivity(); return <div className="content-stack"><div className="page-heading"><div><p className="eyebrow">Workspace / Activity</p><h1>Activity<span className="heading-period">.</span></h1><p className="page-subtitle">A quiet record of what is moving, and when.</p></div></div><section className="panel activity-page-panel">{query.isLoading ? <LoadingState label="Reading the room" /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : query.data?.length ? <div className="activity-page-list">{query.data.map((activity) => <ActivityItem key={activity.id} activity={activity} />)}</div> : <EmptyState title="No activity yet" description="When work starts moving, its trail will appear here." />}</section></div>; }
function SettingsPage() { const { theme, setTheme } = useTheme(); const [saved, setSaved] = useState(false); return <div className="content-stack settings-page"><div className="page-heading"><div><p className="eyebrow">Workspace / Settings</p><h1>Settings<span className="heading-period">.</span></h1><p className="page-subtitle">Set the room up so the work can stay clear.</p></div></div><section className="settings-section"><div className="settings-copy"><h2>Appearance</h2><p>Choose the light for your workbench. This preference stays with you.</p></div><div className="appearance-options"><button className={cx('appearance-card', theme === 'light' && 'appearance-selected')} onClick={() => setTheme('light')} data-testid="button-theme-light"><span className="appearance-preview light-preview"><Sun size={17} /></span><strong>Daylight</strong><small>Warm, paper-like</small></button><button className={cx('appearance-card', theme === 'dark' && 'appearance-selected')} onClick={() => setTheme('dark')} data-testid="button-theme-dark"><span className="appearance-preview dark-preview"><Moon size={17} /></span><strong>After hours</strong><small>Deep, low-glare</small></button></div></section><section className="settings-section"><div className="settings-copy"><h2>Workspace identity</h2><p>The details your team sees when they open Northstar.</p></div><div className="settings-fields"><label>Workspace name<input defaultValue="Northstar" data-testid="input-workspace-name" /></label><label>Workspace description<input defaultValue="Product studio" data-testid="input-workspace-description" /></label><div className="settings-actions"><Button variant="primary" onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 2200); }} data-testid="button-save-settings">{saved ? <><Check size={15} />Saved</> : 'Save preferences'}</Button></div></div></section><section className="settings-section health-section"><div className="settings-copy"><h2>Connection</h2><p>Workbench checks this connection before showing your latest work.</p></div><HealthStatus /></section></div>; }
function HealthStatus() { const query = useHealthCheck({ query: { staleTime: 30000, queryKey: getHealthCheckQueryKey() } }); return <div className="health-card"><span className={cx('health-dot', query.isError && 'health-error')} /><div><strong>{query.isLoading ? 'Checking connection…' : query.isError ? 'Connection needs attention' : 'Workspace is connected'}</strong><small>{query.isError ? 'Try refreshing or check the API service.' : 'Your project data is syncing normally.'}</small></div></div>; }
function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) { return <div className="modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}><div className="modal" role="dialog" aria-modal="true" aria-label={title}><div className="modal-header"><h2>{title}</h2><button className="icon-btn" onClick={onClose} data-testid="button-close-modal" aria-label="Close"><X size={18} /></button></div>{children}</div></div>; }
function ConfirmModal({ title, description, onClose, onConfirm, pending }: { title: string; description: string; onClose: () => void; onConfirm: () => void; pending: boolean }) { return <Modal title={title} onClose={onClose}><div className="confirm-copy"><div className="confirm-icon"><Trash2 size={20} /></div><p>{description}</p></div><div className="modal-actions"><Button onClick={onClose}>Keep it</Button><Button variant="danger" onClick={onConfirm} disabled={pending} data-testid="button-confirm-delete">{pending ? 'Deleting…' : 'Delete task'}</Button></div></Modal>; }

function Router() {
  return (
    // Keep a shared shell (sidebar, navbar) outside the boundary so it
    // survives a page crash.
    <AuthGate>
      <RoutedErrorBoundary>
        <Switch>
          <Route path="/login"><AuthPage mode="login" /></Route>
          <Route path="/register"><AuthPage mode="register" /></Route>
          <Route path="/"><Shell><Overview /></Shell></Route>
          <Route path="/projects"><Shell><ProjectsPage /></Shell></Route>
          <Route path="/projects/:id"><Shell><ProjectDetailPage /></Shell></Route>
          <Route path="/tasks"><Shell><TasksPage /></Shell></Route>
          <Route path="/activity"><Shell><ActivityPage /></Shell></Route>
          <Route path="/settings"><Shell><SettingsPage /></Shell></Route>
          <Route component={NotFound} />
        </Switch>
      </RoutedErrorBoundary>
    </AuthGate>
  );
}

function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <ThemeProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
            <Router />
          </WouterRouter>
        </ThemeProvider>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
