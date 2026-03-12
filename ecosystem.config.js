module.exports = {
  apps : [{
    name: "discord-bot",
    script: "main.py",
    interpreter: "./venv/bin/python3",
    env: {
      PATH: `${process.cwd()}/node_modules/ffmpeg-static:${process.env.PATH}`
    }
  }]
}
