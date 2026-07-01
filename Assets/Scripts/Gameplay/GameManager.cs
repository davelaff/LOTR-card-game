using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Top-level game state manager. Singleton MonoBehaviour.
    /// Orchestrates turn flow, phase transitions, and win/loss conditions.
    /// Mirrors the Python engine/game.py GameState class.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Players")]
        public PlayerManager fpPlayer;
        public PlayerManager shadowPlayer;

        [Header("Systems")]
        public BoardManager board;
        public RingManager ring;

        [Header("Game State")]
        public GamePhase currentPhase = GamePhase.Start;
        public string activePlayer = "fp"; // Free Peoples always first
        public int turnNumber = 1;
        public bool gameOver;
        public string winner;
        public string lossReason;

        [Header("Messages")]
        public List<string> messages = new List<string>();
        public List<string> phaseMessages = new List<string>();

        // --- Singleton ---

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        // --- Setup ---

        /// <summary>
        /// Initialize the game with chosen factions.
        /// TODO: Implement card loading (deck creation, hero placement, opening draw).
        /// </summary>
        public void Setup(Faction fpFaction = Faction.Gondor, Faction shadowFaction = Faction.Mordor)
        {
            // TODO: Create players, load hero cards, create decks, draw opening hands
            messages.Add("GameManager.Setup() — scaffolding only. Game loop TBD.");
        }

        // --- Turn Flow ---

        /// <summary>
        /// Execute the Start Phase: cleanup, untap, willpower, draw, ring start-of-turn.
        /// TODO: Full implementation in game loop phase.
        /// </summary>
        public void StartTurn()
        {
            currentPhase = GamePhase.Start;
            PlayerManager active = GetActivePlayer();
            active.turnNumber++;

            phaseMessages.Clear();
            phaseMessages.Add($"--- {active.playerName}'s Turn {active.turnNumber} ---");

            // TODO: Remove dead allies
            // TODO: Untap all allies + hero
            // TODO: Willpower step
            // TODO: Draw step
            // TODO: Ring start-of-turn
            // TODO: Corruption check
            // TODO: Progress to Main Phase

            currentPhase = GamePhase.Main;
        }

        /// <summary>
        /// Execute the End Phase: ring end-of-turn, clear temp effects, check game over.
        /// TODO: Full implementation in game loop phase.
        /// </summary>
        public void EndTurn()
        {
            currentPhase = GamePhase.End;
            PlayerManager active = GetActivePlayer();

            phaseMessages.Clear();
            phaseMessages.Add($"--- End Phase for {active.playerName} ---");

            // TODO: Ring end-of-turn
            // TODO: Clear temp bonuses from all allies (including heroes)
            // TODO: Switch active player
            // TODO: Check game over conditions

            activePlayer = activePlayer == "fp" ? "shadow" : "fp";
            turnNumber++;

            if (!gameOver)
                phaseMessages.Add($"Turn passes to {(activePlayer == "fp" ? "Free Peoples" : "Shadow")}.");
        }

        // --- Game Over ---

        /// <summary>
        /// Check all loss conditions: influence at 0, corruption at 30.
        /// Returns winner string or null.
        /// TODO: Full implementation in game loop phase.
        /// </summary>
        public string CheckGameOver()
        {
            // TODO: Influence check
            // TODO: Corruption check
            // TODO: Fatigue double-check
            return null;
        }

        // --- Card Play ---

        /// <summary>
        /// Play a card from hand. Returns list of result messages.
        /// TODO: Full implementation in game loop phase.
        /// </summary>
        public List<string> PlayCard(CardData card, string player)
        {
            var msgs = new List<string>();
            msgs.Add("GameManager.PlayCard() — scaffolding only. Game loop TBD.");
            return msgs;
        }

        /// <summary>
        /// Move an ally on the board. Returns list of result messages.
        /// TODO: Full implementation in game loop phase.
        /// </summary>
        public List<string> MoveAlly(BoardAlly ally, string player, int targetLocation, string targetRow = "front")
        {
            var msgs = new List<string>();
            msgs.Add("GameManager.MoveAlly() — scaffolding only. Game loop TBD.");
            return msgs;
        }

        // --- Helpers ---

        public PlayerManager GetActivePlayer()
        {
            return activePlayer == "fp" ? fpPlayer : shadowPlayer;
        }

        public PlayerManager GetEnemyPlayer(string player)
        {
            return player == "fp" ? shadowPlayer : fpPlayer;
        }

        public bool IsShadowFaction(Faction faction)
        {
            return faction == Faction.Mordor
                || faction == Faction.Isengard
                || faction == Faction.Moria
                || faction == Faction.Harad
                || faction == Faction.Nazgul;
        }

        public bool IsFreePeoplesFaction(Faction faction)
        {
            return !IsShadowFaction(faction);
        }
    }

    /// <summary>
    /// Game phase enum — matches Python GamePhase constants.
    /// </summary>
    public enum GamePhase
    {
        Start,
        Main,
        End,
        GameOver
    }
}
