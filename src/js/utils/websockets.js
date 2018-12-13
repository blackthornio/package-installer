// @flow

import Sockette from 'sockette';

import { completeJobStep, completeJob, failJob } from 'jobs/actions';
import {
  completePreflight,
  failPreflight,
  invalidatePreflight,
} from 'plans/actions';
import { invalidateToken } from 'accounts/actions';
import { log } from 'utils/logging';

import type { Dispatch } from 'redux-thunk';
import type { Job } from 'jobs/reducer';
import type { JobStepCompleted, JobCompleted, JobFailed } from 'jobs/actions';
import type { Preflight } from 'plans/reducer';
import type {
  PreflightCompleted,
  PreflightFailed,
  PreflightInvalid,
} from 'plans/actions';
import type { TokenInvalidAction } from 'accounts/actions';

type ErrorEvent = {|
  type: 'BACKEND_ERROR',
  payload: {| message: string |},
|};
type UserEvent = {|
  type: 'USER_TOKEN_INVALID',
|};
type PreflightEvent = {|
  type: 'PREFLIGHT_COMPLETED' | 'PREFLIGHT_FAILED' | 'PREFLIGHT_INVALIDATED',
  payload: Preflight,
|};
type JobEvent = {|
  type: 'TASK_COMPLETED' | 'JOB_COMPLETED' | 'JOB_FAILED',
  payload: Job,
|};
type EventType = ErrorEvent | UserEvent | PreflightEvent | JobEvent;
type Action =
  | TokenInvalidAction
  | PreflightCompleted
  | PreflightFailed
  | PreflightInvalid
  | JobStepCompleted
  | JobCompleted
  | JobFailed;

export const getAction = (event: EventType): Action | null => {
  if (!event || event.type === undefined) {
    return null;
  }
  switch (event.type) {
    case 'USER_TOKEN_INVALID':
      return invalidateToken();
    case 'PREFLIGHT_COMPLETED':
      return completePreflight(event.payload);
    case 'PREFLIGHT_FAILED':
      return failPreflight(event.payload);
    case 'PREFLIGHT_INVALIDATED':
      return invalidatePreflight(event.payload);
    case 'TASK_COMPLETED':
      return completeJobStep(event.payload);
    case 'JOB_COMPLETED':
      return completeJob(event.payload);
    case 'JOB_FAILED':
      return failJob(event.payload);
  }
  return null;
};

export const createSocket = ({
  url,
  options,
  dispatch,
}: {
  url: string,
  options?: { [string]: mixed },
  dispatch: Dispatch,
}): Sockette => {
  const defaults = {
    maxAttempts: 25,
    onopen: () => {},
    onmessage: () => {},
    onreconnect: () => {},
    onmaximum: () => {},
    onclose: () => {},
    onerror: () => {},
  };
  const opts = { ...defaults, ...options };

  return new Sockette(url, {
    protocols: opts.protocols,
    timeout: opts.timeout,
    maxAttempts: opts.maxAttempts,
    onopen: e => {
      log('[WebSocket] connected');
      opts.onopen(e);
    },
    onmessage: e => {
      let data = e.data;
      try {
        data = JSON.parse(e.data);
      } catch (err) {
        // swallow error
      }
      log('[WebSocket] received:', data);
      const action = getAction(data);
      if (action) {
        dispatch(action);
      }
      opts.onmessage(e);
    },
    onreconnect: e => {
      log('[WebSocket] reconnecting...');
      opts.onreconnect(e);
    },
    onmaximum: e => {
      log(`[WebSocket] ending reconnect after ${opts.maxAttempts} attempts`);
      opts.onmaximum(e);
    },
    onclose: e => {
      log('[WebSocket] closed');
      opts.onclose(e);
    },
    onerror: e => {
      log('[WebSocket] error:', e);
      opts.onerror(e);
    },
  });
};
