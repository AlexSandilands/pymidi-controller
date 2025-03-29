# Target install directory
INSTALL_DIR := ~/.local/share/pymidi-controller

.PHONY: install update clean run-dev deploy

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

	@echo "✅ Installed without overwriting user data."

update: install
	@echo "🔄 Updated runtime install."

deploy: install
	@echo "🚀 Restarting pymidi.service..."
	systemctl --user restart pymidi.service
	@echo "✅ Deployed + restarted service."

clean:
	@echo "🧹 Cleaning runtime install..."
	rm -rf $(INSTALL_DIR)
	@echo "✅ Removed $(INSTALL_DIR)"

run-dev:
	@echo "🚀 Running in dev mode (interactive)..."
	python3 midi_run.py --mode interactive
