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
		--exclude 'user_settings' \
		./ $(INSTALL_DIR)

	@echo "📁 Ensuring user_settings/ exists in install dir..."
	mkdir -p $(INSTALL_DIR)/user_settings

	@echo "📄 Copying default user_settings files if missing..."
	@for file in user_settings/* user_settings/.*; do \
		if [ -f $$file ]; then \
			filename=$$(basename $$file); \
			if [ ! -f $(INSTALL_DIR)/user_settings/$$filename ]; then \
				echo " → $$filename"; \
				cp $$file $(INSTALL_DIR)/user_settings/$$filename; \
			fi; \
		fi; \
	done

	@echo "✅ Installed to $(INSTALL_DIR)"


deploy: install
	@echo "🚀 Reloading and deploying systemd user service..."
	@systemctl --user daemon-reload

	@if systemctl --user list-unit-files | grep -q 'pymidi.service'; then \
		if systemctl --user is-active --quiet pymidi.service; then \
			echo "🔁 Service is active — restarting..."; \
			systemctl --user restart pymidi.service; \
		else \
			echo "▶️  Service found but inactive — starting..."; \
			systemctl --user start pymidi.service; \
		fi; \
		if ! systemctl --user is-enabled --quiet pymidi.service; then \
			echo "📌 Service is not enabled — enabling for auto-start at login..."; \
			systemctl --user enable pymidi.service; \
		fi; \
		echo "✅ Service is running and enabled."; \
	else \
		echo "⚠️  Service not found. You may need to create ~/.config/systemd/user/pymidi.service"; \
	fi

clean:
	@echo "🛑 Stopping service (if running)..."
	@systemctl --user stop pymidi.service || true

	@echo "🧹 Cleaning runtime install..."
	rm -rf $(INSTALL_DIR)
	@echo "✅ Removed $(INSTALL_DIR)"

status:
	@systemctl --user status pymidi.service

run-dev:
	@echo "🚀 Running in dev mode (interactive)..."
	python3 pymidi.py --mode interactive
