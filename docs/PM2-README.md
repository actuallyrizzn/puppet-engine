# Using PM2 with Puppet Engine

PM2 is a process manager for Node.js applications that keeps your app running even if it crashes. This guide explains how to use PM2 with Puppet Engine.

## Setup

PM2 should be installed globally:

```bash
npm install -g pm2
```

## Available Commands

We've added several scripts to package.json to make working with PM2 easier:

- `npm run pm2:start` - Start the application using PM2
- `npm run pm2:stop` - Stop the application
- `npm run pm2:restart` - Restart the application
- `npm run pm2:status` - Check the status of all PM2 processes
- `npm run pm2:logs` - View the application logs
- `npm run pm2:monit` - Open the PM2 monitoring dashboard

## Automatic Restart

The PM2 configuration in `ecosystem.config.js` is set up to automatically restart the application when:

1. The application crashes
2. Memory usage exceeds 1GB
3. The application becomes unresponsive

## Logs

All logs are stored in the `logs` directory:

- Standard output: `logs/out.log`
- Error output: `logs/err.log`

## Starting on System Boot

To make PM2 start the application when your system boots:

```bash
pm2 startup
```

Follow the instructions provided by the command, then save your current PM2 configuration:

```bash
pm2 save
```

## Troubleshooting

If the application continues to crash repeatedly, check the logs:

```bash
npm run pm2:logs
```

You can also monitor the application in real-time:

```bash
npm run pm2:monit
```

## Stopping PM2

To stop PM2 completely:

```bash
pm2 kill
``` 