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
	@for file in user_settings/*; do \
		filename=$$(basename $$file); \
		if [ ! -f $(INSTALL_DIR)/user_settings/$$filename ]; then \
			echo " → $$filename"; \
			cp $$file $(INSTALL_DIR)/user_settings/$$filename; \
		fi \
	done

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
	python3 pymidi.py --mode interactive
