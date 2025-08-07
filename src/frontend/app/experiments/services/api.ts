'use client';

import { API_BASE_URL } from '@/app/components/config';
import { DeleteResponse } from '../types';

// --- API Functions ---

export async function deleteDataset(datasetId: string, token: string): Promise<DeleteResponse> {
  try {
    const url = `${API_BASE_URL}/api/v1/datasets/${datasetId}`;
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('Deleting dataset:', url);
    
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    console.log('Dataset delete response status:', res.status);
    console.log('Dataset delete response headers:', res.headers);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      console.log('Dataset delete error data:', errorData);
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: DeleteResponse = await res.json();
    console.log('Dataset delete success data:', data);
    return data;

  } catch (error) {
    console.error("Error deleting dataset:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
}

export async function deleteExperiment(experimentId: string, datasetId: string, token: string): Promise<DeleteResponse> {
  try {
    const url = `${API_BASE_URL}/api/v1/experiments/${experimentId}?dataset_id=${datasetId}`;
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('Deleting experiment:', url);
    
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    console.log('Experiment delete response status:', res.status);
    console.log('Experiment delete response headers:', res.headers);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      console.log('Experiment delete error data:', errorData);
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: DeleteResponse = await res.json();
    console.log('Experiment delete success data:', data);
    return data;

  } catch (error) {
    console.error("Error deleting experiment:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
}
