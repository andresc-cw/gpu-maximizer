/**
 * Audio Manager for GPU Tycoon
 * Handles sound effects using Web Audio API
 */

class AudioManager {
    constructor() {
        this.context = null;
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.3;
        
        // Initialize on user interaction (required by browsers)
        document.addEventListener('click', () => this.initialize(), { once: true });
    }
    
    initialize() {
        if (this.context) return;
        
        try {
            this.context = new (window.AudioContext || window.webkitAudioContext)();
            console.log('🔊 Audio initialized');
        } catch (e) {
            console.warn('Audio not supported:', e);
            this.enabled = false;
        }
    }
    
    /**
     * Play a simple beep sound
     */
    playBeep(frequency = 440, duration = 0.1, type = 'sine') {
        if (!this.enabled || !this.context) return;
        
        const oscillator = this.context.createOscillator();
        const gainNode = this.context.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.context.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(this.volume, this.context.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.context.currentTime + duration);
        
        oscillator.start(this.context.currentTime);
        oscillator.stop(this.context.currentTime + duration);
    }
    
    /**
     * Job completed sound - pleasant ding
     */
    jobComplete() {
        this.playBeep(880, 0.1, 'sine');
        setTimeout(() => this.playBeep(1047, 0.1, 'sine'), 50);
    }
    
    /**
     * Purchase sound - success chime
     */
    purchase() {
        this.playBeep(523, 0.08, 'square');
        setTimeout(() => this.playBeep(659, 0.08, 'square'), 60);
        setTimeout(() => this.playBeep(784, 0.12, 'square'), 120);
    }
    
    /**
     * SLA miss alert - warning beep
     */
    alert() {
        this.playBeep(220, 0.15, 'sawtooth');
        setTimeout(() => this.playBeep(220, 0.15, 'sawtooth'), 200);
    }
    
    /**
     * Event notification - special sound
     */
    event() {
        this.playBeep(440, 0.1, 'triangle');
        setTimeout(() => this.playBeep(554, 0.1, 'triangle'), 80);
        setTimeout(() => this.playBeep(659, 0.15, 'triangle'), 160);
    }
    
    /**
     * Achievement unlock - fanfare
     */
    achievement() {
        this.playBeep(523, 0.1, 'sine');
        setTimeout(() => this.playBeep(659, 0.1, 'sine'), 100);
        setTimeout(() => this.playBeep(784, 0.1, 'sine'), 200);
        setTimeout(() => this.playBeep(1047, 0.2, 'sine'), 300);
    }
    
    /**
     * Toggle audio on/off
     */
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
    
    /**
     * Set volume (0 to 1)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
    }
}

// Global audio manager instance
const audioManager = new AudioManager();

