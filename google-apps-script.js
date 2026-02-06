// ============================================
// GOOGLE APPS SCRIPT v2 - UPDATED FOR BETTER SYNC
// ============================================
//
// SETUP INSTRUCTIONS:
// 1. Go to your Google Apps Script editor
// 2. Delete ALL existing code
// 3. Paste this ENTIRE file
// 4. Click "Deploy" > "Manage deployments"
// 5. Click the pencil icon to edit
// 6. Change version to "New version"
// 7. Click Deploy
//
// ============================================

const BATCHES_SHEET = 'Batches';
const LOGS_SHEET = 'Logs';
const SPREADSHEET_ID = '10f54LuRTrYDLCHH8ur3zmdaL_p1ul5UiL7HXoNkA77c';

function initSheets() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  let batchesSheet = ss.getSheetByName(BATCHES_SHEET);
  if (!batchesSheet) {
    batchesSheet = ss.insertSheet(BATCHES_SHEET);
    batchesSheet.getRange(1, 1, 1, 14).setValues([[
      'id', 'name', 'sensor', 'totalFrames', 'completed', 'startFrame', 'endFrame',
      'currentFrame', 'status', 'startDate', 'delivered', 'deliveredDate', 'paid', 'paidDate'
    ]]);
    batchesSheet.getRange(1, 1, 1, 14).setFontWeight('bold');
  }

  let logsSheet = ss.getSheetByName(LOGS_SHEET);
  if (!logsSheet) {
    logsSheet = ss.insertSheet(LOGS_SHEET);
    logsSheet.getRange(1, 1, 1, 9).setValues([[
      'id', 'date', 'batchId', 'batchName', 'annotator', 'workType', 'frames', 'startFrame', 'endFrame'
    ]]);
    logsSheet.getRange(1, 1, 1, 9).setFontWeight('bold');
  }

  return { batchesSheet, logsSheet };
}

// Handle ALL requests via GET (works better with CORS)
function doGet(e) {
  const { batchesSheet, logsSheet } = initSheets();
  const action = e.parameter.action || 'getAll';
  const dataParam = e.parameter.data;

  let result;

  try {
    // Parse data if provided
    let data = {};
    if (dataParam) {
      data = JSON.parse(dataParam);
    }

    switch(action) {
      case 'getAll':
        result = {
          success: true,
          batches: getSheetData(batchesSheet),
          logs: getSheetData(logsSheet)
        };
        break;

      case 'addBatch':
        addBatch(batchesSheet, data.batch);
        result = { success: true };
        break;

      case 'updateBatch':
        updateBatch(batchesSheet, data.batch);
        result = { success: true };
        break;

      case 'deleteBatch':
        deleteBatch(batchesSheet, data.id);
        // Also delete related logs
        deleteLogsByBatchId(logsSheet, data.id);
        result = { success: true };
        break;

      case 'addLog':
        addLog(logsSheet, data.log);
        result = { success: true };
        break;

      case 'updateLog':
        updateLog(logsSheet, data.log);
        result = { success: true };
        break;

      case 'deleteLog':
        deleteLog(logsSheet, data.id);
        result = { success: true };
        break;

      case 'saveAll':
        saveBatches(batchesSheet, data.batches);
        saveLogs(logsSheet, data.logs);
        result = { success: true };
        break;

      default:
        result = { success: false, error: 'Unknown action: ' + action };
    }
  } catch (error) {
    result = { success: false, error: error.toString() };
  }

  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

// Also support POST for backwards compatibility
function doPost(e) {
  const { batchesSheet, logsSheet } = initSheets();
  let result;

  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;

    switch(action) {
      case 'addBatch':
        addBatch(batchesSheet, data.batch);
        result = { success: true };
        break;

      case 'updateBatch':
        updateBatch(batchesSheet, data.batch);
        result = { success: true };
        break;

      case 'deleteBatch':
        deleteBatch(batchesSheet, data.id);
        deleteLogsByBatchId(logsSheet, data.id);
        result = { success: true };
        break;

      case 'addLog':
        addLog(logsSheet, data.log);
        result = { success: true };
        break;

      case 'updateLog':
        updateLog(logsSheet, data.log);
        result = { success: true };
        break;

      case 'deleteLog':
        deleteLog(logsSheet, data.id);
        result = { success: true };
        break;

      case 'saveAll':
        saveBatches(batchesSheet, data.batches);
        saveLogs(logsSheet, data.logs);
        result = { success: true };
        break;

      default:
        result = { success: false, error: 'Unknown action' };
    }
  } catch (error) {
    result = { success: false, error: error.toString() };
  }

  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

function getSheetData(sheet) {
  const data = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];

  const headers = data[0];
  const rows = data.slice(1);

  return rows.map(row => {
    const obj = {};
    headers.forEach((header, i) => {
      let value = row[i];
      if (value === 'TRUE' || value === true) value = true;
      else if (value === 'FALSE' || value === false) value = false;
      else if (typeof value === 'string' && !isNaN(value) && value !== '' && !value.includes('-')) {
        value = Number(value);
      }
      obj[header] = value;
    });
    return obj;
  }).filter(obj => obj.id); // Filter out empty rows
}

function addBatch(sheet, batch) {
  const row = [
    String(batch.id), batch.name, batch.sensor, batch.totalFrames || 0, batch.completed || 0,
    batch.startFrame || 0, batch.endFrame || 0, batch.currentFrame || 0, batch.status || 'not-starting',
    batch.startDate || '', batch.delivered || false, batch.deliveredDate || '',
    batch.paid || false, batch.paidDate || ''
  ];
  sheet.appendRow(row);
}

function updateBatch(sheet, batch) {
  const data = sheet.getDataRange().getValues();
  const batchId = String(batch.id);

  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]) === batchId) {
      sheet.getRange(i + 1, 1, 1, 14).setValues([[
        batchId, batch.name, batch.sensor, batch.totalFrames || 0, batch.completed || 0,
        batch.startFrame || 0, batch.endFrame || 0, batch.currentFrame || 0, batch.status || 'not-starting',
        batch.startDate || '', batch.delivered || false, batch.deliveredDate || '',
        batch.paid || false, batch.paidDate || ''
      ]]);
      return { success: true };
    }
  }
  // If not found, add it
  addBatch(sheet, batch);
  return { success: true };
}

function deleteBatch(sheet, id) {
  const data = sheet.getDataRange().getValues();
  const batchId = String(id);

  for (let i = data.length - 1; i >= 1; i--) {
    if (String(data[i][0]) === batchId) {
      sheet.deleteRow(i + 1);
      return { success: true };
    }
  }
  return { success: true };
}

function addLog(sheet, log) {
  const row = [
    String(log.id), log.date, String(log.batchId), log.batchName || '',
    log.annotator, log.workType || 'production', log.frames || 0,
    log.startFrame || '', log.endFrame || ''
  ];
  sheet.appendRow(row);
}

function updateLog(sheet, log) {
  const data = sheet.getDataRange().getValues();
  const logId = String(log.id);

  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]) === logId) {
      sheet.getRange(i + 1, 1, 1, 9).setValues([[
        logId, log.date, String(log.batchId), log.batchName || '',
        log.annotator, log.workType || 'production', log.frames || 0,
        log.startFrame || '', log.endFrame || ''
      ]]);
      return { success: true };
    }
  }
  return { success: false, error: 'Log not found' };
}

function deleteLog(sheet, id) {
  const data = sheet.getDataRange().getValues();
  const logId = String(id);

  for (let i = data.length - 1; i >= 1; i--) {
    if (String(data[i][0]) === logId) {
      sheet.deleteRow(i + 1);
      return { success: true };
    }
  }
  return { success: true };
}

function deleteLogsByBatchId(sheet, batchId) {
  const data = sheet.getDataRange().getValues();
  const id = String(batchId);

  // Delete from bottom to top to avoid index issues
  for (let i = data.length - 1; i >= 1; i--) {
    if (String(data[i][2]) === id) {
      sheet.deleteRow(i + 1);
    }
  }
}

function saveBatches(sheet, batches) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, 14).clearContent();
  }

  if (!batches || batches.length === 0) return;

  const rows = batches.map(b => [
    String(b.id), b.name, b.sensor, b.totalFrames || 0, b.completed || 0,
    b.startFrame || 0, b.endFrame || 0, b.currentFrame || 0, b.status || 'not-starting',
    b.startDate || '', b.delivered || false, b.deliveredDate || '',
    b.paid || false, b.paidDate || ''
  ]);

  sheet.getRange(2, 1, rows.length, 14).setValues(rows);
}

function saveLogs(sheet, logs) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, 9).clearContent();
  }

  if (!logs || logs.length === 0) return;

  const rows = logs.map(l => [
    String(l.id), l.date, String(l.batchId), l.batchName || '',
    l.annotator, l.workType || 'production', l.frames || 0,
    l.startFrame || '', l.endFrame || ''
  ]);

  sheet.getRange(2, 1, rows.length, 9).setValues(rows);
}

// Run this once to add default data
function initWithDefaultData() {
  const { batchesSheet } = initSheets();

  const defaultBatches = [
    ['1', '10000_13000', 'camera1', 3000, 3000, 10000, 13000, 13000, 'completed', '2025-01-10', false, '', false, ''],
    ['4', '6400_7000', 'camera1', 600, 200, 6400, 7000, 6600, 'running', '2025-01-15', false, '', false, ''],
    ['7', '7000_10000', 'camera1', 3000, 0, 7000, 10000, 7000, 'not-starting', '', false, '', false, ''],
    ['2', '10000_12000', 'camera0', 2000, 2000, 10000, 12000, 12000, 'completed', '2025-01-08', false, '', false, ''],
    ['5', '12000_13000', 'camera0', 1000, 0, 12000, 13000, 12000, 'running', '2025-01-18', false, '', false, ''],
    ['8', '6400_10000', 'camera0', 3600, 0, 6400, 10000, 6400, 'not-starting', '', false, '', false, ''],
    ['3', '10000_11000', 'lidar', 1000, 1000, 10000, 11000, 11000, 'completed', '2025-01-05', false, '', false, ''],
    ['6', '11000_12000', 'lidar', 1000, 0, 11000, 12000, 11000, 'running', '2025-01-17', false, '', false, ''],
    ['9', '12000_13000', 'lidar', 1000, 0, 12000, 13000, 12000, 'not-starting', '', false, '', false, ''],
    ['10', '7000_10000', 'lidar', 3000, 0, 7000, 10000, 7000, 'not-starting', '', false, '', false, '']
  ];

  batchesSheet.getRange(2, 1, defaultBatches.length, 14).setValues(defaultBatches);
  return 'Default data initialized!';
}
