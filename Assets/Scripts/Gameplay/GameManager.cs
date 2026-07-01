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
        /// TODO: Card library loading (deck creation, hero placement, opening draw).
        /// </summary>
        public void Setup(Faction fpFaction = Faction.Gondor, Faction shadowFaction = Faction.Mordor)
        {
            string fpName = $"Free Peoples ({fpFaction})";
            string shadowName = $"Shadow ({shadowFaction})";

            fpPlayer.playerName = fpName;
            fpPlayer.faction = fpFaction;
            fpPlayer.isFreePeoples = true;

            shadowPlayer.playerName = shadowName;
            shadowPlayer.faction = shadowFaction;
            shadowPlayer.isFreePeoples = false;

            board.Initialize();

            // TODO: Load hero cards from ScriptableObjects, create deck, draw opening hands
            // TODO: Deploy heroes to board, set initial willpower

            messages.Clear();
            messages.Add("Game setup complete!");
            messages.Add($"{fpName} vs {shadowName}");
        }

        // --- Turn Flow ---

        /// <summary>
        /// Execute the Start Phase: cleanup, untap, willpower, draw, ring start-of-turn.
        /// </summary>
        public void StartTurn()
        {
            currentPhase = GamePhase.Start;
            PlayerManager active = GetActivePlayer();
            active.turnNumber++;

            phaseMessages.Clear();
            phaseMessages.Add($"--- {active.playerName}'s Turn {active.turnNumber} ---");
            phaseMessages.Add($"Phase: {GamePhase.Start}");

            // Remove dead allies from all locations and deployment zones
            CleanupDeadAllies();

            // Untap all allies at locations
            int untapped = 0;
            foreach (var loc in board.locations)
            {
                foreach (var ally in loc.GetAllies(activePlayer))
                {
                    ally.Untap();
                    untapped++;
                }
            }

            // Untap allies in deployment zone
            List<BoardAlly> deployZone = activePlayer == "fp"
                ? board.fpDeployment : board.shadowDeployment;
            foreach (var ally in deployZone)
            {
                ally.Untap();
                untapped++;
            }

            // Untap hero
            if (active.hero != null && active.hero.IsAlive)
            {
                active.hero.Untap();
                active.hero.hasUsedAbilityThisTurn = false;
            }

            phaseMessages.Add($"Untapped {untapped} allies + Hero.");

            // Willpower step
            if (active.turnNumber == 1)
                active.willpowerMax = 1; // Both players start with 1 WP on turn 1
            else if (active.willpowerMax < 10)
                active.willpowerMax++;

            active.willpowerPool = active.EffectiveWillpowerMax;
            phaseMessages.Add(
                $"Willpower: {active.willpowerPool}/{active.EffectiveWillpowerMax}");

            // Draw step — active player draws 1 card
            CardData drawn = active.DrawCard();
            if (drawn != null)
                phaseMessages.Add($"Drew {drawn.DisplayName}.");

            // Ring start-of-turn
            ring.StartTurn();

            // Corruption check
            phaseMessages.Add($"Ring: {ring.GetCorruptionStatus()}");

            // Progress to Main Phase
            currentPhase = GamePhase.Main;
            phaseMessages.Add($"Phase: {GamePhase.Main}");
        }

        /// <summary>
        /// Execute the End Phase: ring end-of-turn, clear temp effects, check game over.
        /// </summary>
        public void EndTurn()
        {
            currentPhase = GamePhase.End;
            PlayerManager active = GetActivePlayer();

            phaseMessages.Clear();
            phaseMessages.Add($"--- {GamePhase.End} for {active.playerName} ---");

            // Ring end-of-turn
            ring.EndTurn(activePlayer);

            // Clear temporary effects from all allies at locations
            foreach (var loc in board.locations)
            {
                foreach (string pid in new[] { "fp", "shadow" })
                {
                    foreach (var ally in loc.GetAllies(pid))
                        ally.ClearTempBonuses();
                }
            }

            // Clear temp from deployment zones
            foreach (var ally in board.fpDeployment)
                ally.ClearTempBonuses();
            foreach (var ally in board.shadowDeployment)
                ally.ClearTempBonuses();

            // Clear hero temp bonuses
            if (fpPlayer.hero != null)
                fpPlayer.hero.ClearTempBonuses();
            if (shadowPlayer.hero != null)
                shadowPlayer.hero.ClearTempBonuses();

            phaseMessages.Add("Temporary effects expire.");

            // Switch active player
            activePlayer = activePlayer == "fp" ? "shadow" : "fp";
            turnNumber++;

            // Check game over conditions
            CheckGameOver();

            if (!gameOver)
            {
                phaseMessages.Add(
                    $"Turn passes to {(activePlayer == "fp" ? "Free Peoples" : "Shadow")}.");
            }
        }

        // --- Game Over ---

        /// <summary>
        /// Check all loss conditions: influence at 0, corruption at 30, fatigue.
        /// </summary>
        public void CheckGameOver()
        {
            // Influence check
            if (fpPlayer.IsDefeated())
            {
                gameOver = true;
                winner = "shadow";
                lossReason = "Free Peoples' Influence reduced to 0!";
                currentPhase = GamePhase.GameOver;
                phaseMessages.Add($"GAME OVER: {lossReason}");
                return;
            }

            if (shadowPlayer.IsDefeated())
            {
                gameOver = true;
                winner = "fp";
                lossReason = "Shadow's Influence reduced to 0!";
                currentPhase = GamePhase.GameOver;
                phaseMessages.Add($"GAME OVER: {lossReason}");
                return;
            }

            // Corruption check
            string corruptionLoser = ring.CheckCorruptionLoss();
            if (corruptionLoser != null)
            {
                gameOver = true;
                winner = corruptionLoser == "fp" ? "shadow" : "fp";
                lossReason = $"Corruption reached 30! " +
                    $"{(corruptionLoser == "fp" ? "Free Peoples" : "Shadow")} loses!";
                currentPhase = GamePhase.GameOver;
                phaseMessages.Add($"GAME OVER: {lossReason}");
                return;
            }

            // Fatigue double-check (deck exhaustion can reduce influence below zero)
            if (fpPlayer.influence <= 0)
            {
                gameOver = true;
                winner = "shadow";
                lossReason = "Free Peoples' Influence reduced to 0 (fatigue)!";
                currentPhase = GamePhase.GameOver;
                return;
            }

            if (shadowPlayer.influence <= 0)
            {
                gameOver = true;
                winner = "fp";
                lossReason = "Shadow's Influence reduced to 0 (fatigue)!";
                currentPhase = GamePhase.GameOver;
                return;
            }
        }

        // --- Card Play ---

        /// <summary>
        /// Play a card from hand. Returns list of result messages.
        /// Dispatches by card type: Ally, Event, Artifact, Location.
        /// </summary>
        public List<string> PlayCard(CardData card, string player)
        {
            var msgs = new List<string>();
            PlayerManager playerState = GetPlayerState(player);

            // Check willpower
            if (!playerState.SpendWillpower(card.cost))
            {
                msgs.Add($"Not enough Willpower! Need {card.cost}, " +
                    $"have {playerState.willpowerPool}.");
                return msgs;
            }

            // Remove from hand
            if (!playerState.PlayCard(card))
            {
                msgs.Add("Card not in hand!");
                // Refund willpower
                playerState.AddWillpower(card.cost);
                return msgs;
            }

            msgs.Add($"Played {card.DisplayName} for {card.cost} WP.");

            switch (card.cardType)
            {
                case CardType.Ally:
                    var ally = new BoardAlly
                    {
                        card = card,
                        currentToughness = card.toughness,
                        turnEntered = playerState.turnNumber,
                        tapped = true // Summoning sickness
                    };

                    if (ally.HasCharge)
                        ally.tapped = false;

                    board.DeployAlly(ally, player);
                    msgs.Add($"{card.cardName} enters deployment zone.");

                    if (ally.HasAmbush)
                        msgs.Add("Ambush: can deploy directly to contested location (auto for AI).");

                    // TODO: Resolve on-enter effects via EffectResolver (step 4)
                    break;

                case CardType.Event:
                    // TODO: Resolve event via EventResolver (step 4)
                    // For now: events go directly to discard
                    playerState.discard.Add(card);
                    msgs.Add($"{card.cardName} resolves and goes to discard.");
                    break;

                case CardType.Artifact:
                    if (playerState.hero != null && playerState.hero.IsAlive)
                    {
                        playerState.hero.artifacts.Add(card);
                        msgs.Add($"{card.cardName} attached to {playerState.hero.card.cardName}.");
                    }
                    else
                    {
                        msgs.Add("No hero to attach artifact to!");
                        playerState.discard.Add(card);
                    }
                    break;

                case CardType.Location:
                    bool placed = false;
                    for (int i = 0; i < board.locations.Count; i++)
                    {
                        if (board.locations[i].IsEmpty)
                        {
                            board.PlayLocation(card, player, i);
                            msgs.Add($"{card.cardName} placed at Location Slot {i + 1} " +
                                $"(Def {card.defense}).");
                            placed = true;
                            break;
                        }
                    }
                    if (!placed)
                    {
                        msgs.Add("No empty location slots available!");
                        playerState.discard.Add(card);
                    }
                    break;
            }

            return msgs;
        }

        // --- Ally Movement ---

        /// <summary>
        /// Move an ally on the board. Returns list of result messages.
        /// </summary>
        public List<string> MoveAlly(BoardAlly ally, string player,
            int targetLocation, string targetRow = "front")
        {
            var msgs = new List<string>();
            int? currentLocIndex = board.FindAllyLocation(ally, player);

            if (currentLocIndex == null)
            {
                msgs.Add("Ally not found on board!");
                return msgs;
            }

            int current = currentLocIndex.Value;

            // Can the ally move?
            if (!ally.CanMove() && current != -1)
            {
                msgs.Add($"{ally.card.cardName} cannot move (tapped or already acted)!");
                return msgs;
            }

            bool success = false;

            if (current == -1)
            {
                // From deployment to location
                success = board.MoveAllyToLocation(ally, player, targetLocation, targetRow);
                if (success)
                    msgs.Add($"{ally.card.cardName} moves to Location {targetLocation + 1} ({targetRow}).");
            }
            else if (current == targetLocation)
            {
                // Row swap at same location
                success = board.MoveAllyBetweenRows(ally, player, targetLocation, targetRow);
                if (success)
                    msgs.Add($"{ally.card.cardName} moves to {targetRow} line at Location {targetLocation + 1}.");
                else
                    msgs.Add("Already in that row or move failed.");
            }
            else
            {
                // Between locations
                success = board.MoveAllyBetweenLocations(ally, player, current, targetLocation, targetRow);
                if (success)
                    msgs.Add($"{ally.card.cardName} moves from Location {current + 1} to {targetLocation + 1}.");
            }

            if (!success && current != -1)
            {
                msgs.Add("Move failed — row may be full or not adjacent.");
                return msgs;
            }

            // Movement costs the ally's action
            ally.tapped = true;
            ally.hasMovedThisTurn = true;

            return msgs;
        }

        // --- Helpers ---

        public PlayerManager GetActivePlayer()
        {
            return activePlayer == "fp" ? fpPlayer : shadowPlayer;
        }

        public PlayerManager GetPlayerState(string player)
        {
            return player == "fp" ? fpPlayer : shadowPlayer;
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

        // --- Internal ---

        /// <summary>
        /// Remove dead allies from all locations and deployment zones for both players.
        /// Moves their cards to the owning player's discard pile.
        /// </summary>
        private void CleanupDeadAllies()
        {
            var fpDead = board.RemoveDeadAllies("fp");
            foreach (var dead in fpDead)
                fpPlayer.discard.Add(dead.card);

            var shadowDead = board.RemoveDeadAllies("shadow");
            foreach (var dead in shadowDead)
                shadowPlayer.discard.Add(dead.card);
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
