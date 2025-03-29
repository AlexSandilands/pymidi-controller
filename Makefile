INSTALL_DIR := ~/.local/share/pymidi-controller

.PHONY: setup install deploy clean listen run-dev

setup:
	@echo "🔧 Running configuration setup..."
	python3 cli.py hue-discover || true
	python3 cli.py elgato-discover || true
	@echo "🎛️ You can now run 'make listen' to configure MIDI mappings."

listen:
	@echo "🎹 Starting interactive MIDI listener..."
	python3 midi_listener.py

install:
	@echo "📦 Installing to $(INSTALL_DIR)..."
	mkdir -p $(INSTALL_DIR)
	rsync -av \
		--exclude '.git' \
		--exclude '__pycache__' \
		--exclude '*.pyc' \
		--exclude 'midi_bindings.json' \
		--exclude '.env' \
		./ $(INSTALL_DIR)

	@if [ ! -f $(INSTALL_DIR)/midi_bindings.json ]; then \
		echo "📄 Copying default midi_bindings.json..."; \
		cp midi_bindings.json $(INSTALL_DIR)/midi_bindings.json; \
	fi

	@if [ ! -f $(INSTALL_DIR)/.env ]; then \
		echo "🔐 Copying default .env..."; \
		cp .env $(INSTALL_DIR)/.env; \
	fi

	@echo "✅ Installed to $(INSTALL_DIR)"

deploy: install
	@echo "🚀 Restarting pymidi.service if it exists..."
	@systemctl --user daemon-reload
	@if systemctl --user list-units --type=service | grep -q pymidi.service; then \
		systemctl --user restart pymidi.service; \
		echo "✅ Service restarted."; \
	else \
		echo "⚠️  Service not found. You may need to enable it manually."; \
	fi

clean:
	@echo "🧹 Cleaning runtime install..."
	rm -rf $(INSTALL_DIR)
	@echo "✅ Removed $(INSTALL_DIR)"

run-dev:
	@echo "🚀 Running in dev mode (interactive)..."
	python3 midi_run.py --mode interactive
