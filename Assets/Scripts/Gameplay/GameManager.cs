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

        // Resolvers (initialized in Setup)
        [System.NonSerialized]
        public CombatResolver combat;
        [System.NonSerialized]
        public EffectResolver effects;
        [System.NonSerialized]
        public EventResolver events;

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

        // Input mode state
        private enum InputMode { Normal, Attacking }
        private InputMode inputMode = InputMode.Normal;
        private List<BoardAlly> availableAttackers = new List<BoardAlly>();
        private int lastInputFrame = -999;
        private KeyCode pendingKey = KeyCode.None;

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

            // Auto-create child managers if not assigned in Inspector
            EnsureManager(ref fpPlayer, "FP Player");
            EnsureManager(ref shadowPlayer, "Shadow Player");
            EnsureManager(ref board, "Board");
            EnsureManager(ref ring, "Ring");
        }

        /// <summary>
        /// If manager ref is null, create a child GameObject with the component.
        /// </summary>
        private void EnsureManager<T>(ref T manager, string name) where T : MonoBehaviour
        {
            if (manager != null) return;
            var child = new GameObject(name);
            child.transform.SetParent(transform);
            manager = child.AddComponent<T>();
        }

        private bool setupCalled;

        private void Start()
        {
            // Auto-setup Gondor vs Mordor for testing
            if (!setupCalled)
            {
                Setup();
                Debug.Log("[GameManager] Auto-starting first turn...");
                StartTurn();
                DumpHand();
            }
        }

        // --- Setup ---

        /// <summary>
        /// Initialize the game with chosen factions.
        /// TODO: Card library loading (deck creation, hero placement, opening draw).
        /// </summary>
        public void Setup(Faction fpFaction = Faction.Gondor, Faction shadowFaction = Faction.Mordor)
        {
            setupCalled = true;
            string fpName = $"Free Peoples ({fpFaction})";
            string shadowName = $"Shadow ({shadowFaction})";

            fpPlayer.playerName = fpName;
            fpPlayer.faction = fpFaction;
            fpPlayer.isFreePeoples = true;

            shadowPlayer.playerName = shadowName;
            shadowPlayer.faction = shadowFaction;
            shadowPlayer.isFreePeoples = false;

            board.Initialize();

            // Initialize resolvers
            combat = new CombatResolver(this);
            effects = new EffectResolver(this);
            events = new EventResolver(this, effects);

            // --- Card library & deck building ---
            CardLibrary.Initialize();

            // Load and deploy heroes
            var fpHero = SetupHero(fpPlayer, fpPlayer.faction, "fp");
            var shadowHero = SetupHero(shadowPlayer, shadowPlayer.faction, "shadow");

            // Build faction decks (all non-hero cards)
            fpPlayer.deck = new List<CardData>(CardLibrary.GetDeckCards(fpPlayer.faction));
            shadowPlayer.deck = new List<CardData>(CardLibrary.GetDeckCards(shadowPlayer.faction));

            // Shuffle and draw opening hands
            fpPlayer.ShuffleDeck();
            shadowPlayer.ShuffleDeck();
            fpPlayer.DrawCards(7);
            shadowPlayer.DrawCards(7);

            // Willpower: max starts at 0, incremented to 1 on first StartTurn
            fpPlayer.willpowerMax = 0;
            shadowPlayer.willpowerMax = 0;

            messages.Clear();
            messages.Add("Game setup complete!");
            messages.Add($"{fpName} vs {shadowName}");
            messages.Add($"Heroes: {fpHero} vs {shadowHero}");
            messages.Add($"Decks: {fpPlayer.deck.Count} FP, {shadowPlayer.deck.Count} Shadow");
            messages.Add($"Opening hands: 7 cards each.");

            // Console dump for verification
            Debug.Log($"[Setup] {fpName} vs {shadowName}");
            Debug.Log($"[Setup] Heroes: {fpHero} vs {shadowHero}");
            Debug.Log($"[Setup] Decks: {fpPlayer.deck.Count} FP cards, {shadowPlayer.deck.Count} Shadow cards");
            Debug.Log($"[Setup] FP hand: {string.Join(", ", fpPlayer.hand.ConvertAll(c => c.cardName))}");
            Debug.Log($"[Setup] Shadow hand: {string.Join(", ", shadowPlayer.hand.ConvertAll(c => c.cardName))}");
        }

        /// <summary>
        /// Load a faction's hero card from the library and deploy it.
        /// Returns the hero's display name or "None" if no hero found.
        /// </summary>
        private string SetupHero(PlayerManager player, Faction faction, string playerId)
        {
            CardData heroData = CardLibrary.GetHero(faction);
            if (heroData == null)
            {
                Debug.LogWarning($"[GameManager] No hero found for faction {faction}");
                player.leaderless = true;
                return "None";
            }

            var heroAlly = new BoardAlly
            {
                card = heroData,
                currentToughness = heroData.toughness,
                turnEntered = 0,
                tapped = false
            };

            player.hero = heroAlly;

            // Deploy hero to deployment zone
            if (playerId == "fp")
                board.fpDeployment.Add(heroAlly);
            else
                board.shadowDeployment.Add(heroAlly);

            player.leaderless = false;
            return heroData.cardName;
        }

        // --- Player Input ---

        private void Update()
        {
            if (!setupCalled || gameOver) return;

            // Process input from OnGUI event capture (bypasses Input System focus issues)
            var key = pendingKey;
            pendingKey = KeyCode.None;

            if (key == KeyCode.None) return;

            // Esc always cancels input mode
            if (key == KeyCode.Escape)
            {
                if (inputMode != InputMode.Normal)
                {
                    inputMode = InputMode.Normal;
                    Debug.Log("[Input] Canceled.");
                }
                return;
            }

            // Attacking mode: select attacker by number
            if (inputMode == InputMode.Attacking)
            {
                if (key >= KeyCode.Alpha1 && key <= KeyCode.Alpha9)
                {
                    int idx = (int)key - (int)KeyCode.Alpha1;
                    if (idx < availableAttackers.Count)
                    {
                        ExecuteAttack(availableAttackers[idx]);
                        inputMode = InputMode.Normal;
                    }
                    else
                    {
                        Debug.Log($"[Attack] Invalid index {idx + 1}. Esc to cancel.");
                    }
                }
                return;
            }

            // Normal mode
            if (key == KeyCode.Space)
            {
                if (currentPhase == GamePhase.Start || currentPhase == GamePhase.End)
                {
                    StartTurn();
                    DumpHand();
                    DumpPhase();
                }
                else
                {
                    Debug.Log($"[Input] Already in {currentPhase} phase. Press E to end turn.");
                }
                return;
            }

            if (key == KeyCode.E)
            {
                if (currentPhase == GamePhase.Main)
                {
                    EndTurn();
                    DumpPhase();
                }
                else
                {
                    Debug.Log($"[Input] Not in Main phase. Press Space to start a turn.");
                }
                return;
            }

            if (key == KeyCode.H)
            {
                DumpHand();
                return;
            }

            if (key == KeyCode.B)
            {
                DumpBoard();
                return;
            }

            if (key == KeyCode.A)
            {
                EnterAttackMode();
                return;
            }

            // 1-9: play card from hand
            if (key >= KeyCode.Alpha1 && key <= KeyCode.Alpha9)
            {
                PlayCardFromHand((int)key - (int)KeyCode.Alpha1);
            }
        }

        // --- Console Output ---

        private void DumpPhase()
        {
            foreach (var msg in phaseMessages)
                Debug.Log($"[Phase] {msg}");
        }

        private void OnGUI()
        {
            if (!setupCalled) return;

            // Detect any keyboard input via IMGUI event system
            Event e = Event.current;
            if (e != null && e.isKey && e.type == EventType.KeyDown)
            {
                lastInputFrame = Time.frameCount;
                pendingKey = e.keyCode;
            }

            float y = 10;
            GUI.Box(new Rect(10, y, 400, gameOver ? 80 : 200), "");
            y += 10;

            var style = new GUIStyle(GUI.skin.label);
            style.fontSize = 16;
            style.normal.textColor = Color.white;

            var active = GetActivePlayer();
            GUI.Label(new Rect(20, y, 380, 25), $"Turn {active.turnNumber} — {active.playerName}", style);
            y += 22;

            var phaseStyle = new GUIStyle(GUI.skin.label);
            phaseStyle.fontSize = 14;
            phaseStyle.normal.textColor = currentPhase == GamePhase.Main ? Color.green : Color.yellow;
            GUI.Label(new Rect(20, y, 380, 20), $"Phase: {currentPhase}  WP: {active.willpowerPool}/{active.EffectiveWillpowerMax}  Hand: {active.hand.Count}", phaseStyle);
            y += 22;

            var helpStyle = new GUIStyle(GUI.skin.label);
            helpStyle.fontSize = 11;
            helpStyle.normal.textColor = Color.gray;

            if (gameOver)
            {
                var goStyle = new GUIStyle(GUI.skin.label);
                goStyle.fontSize = 18;
                goStyle.normal.textColor = Color.red;
                GUI.Label(new Rect(20, y, 380, 25), $"GAME OVER — {lossReason}", goStyle);
                return;
            }

            if (inputMode == InputMode.Attacking)
            {
                GUI.Label(new Rect(20, y, 380, 16), "[ATTACK MODE] Select attacker (1-9) or Esc to cancel", helpStyle);
                y += 18;
            }

            GUI.Label(new Rect(20, y, 380, 14), "Space:Start  E:End  H:Hand  B:Board  A:Attack  1-9:Play", helpStyle);
            y += 16;
            GUI.Label(new Rect(20, y, 380, 14), $"Influence: FP {fpPlayer.influence}  Shadow {shadowPlayer.influence}  Ring: {ring.GetCorruptionStatus()}", helpStyle);
            y += 18;

            // Focus nag: show if no input detected for 3 seconds
            if (Time.frameCount - lastInputFrame > 180)
            {
                var focusStyle = new GUIStyle(GUI.skin.label);
                focusStyle.fontSize = 14;
                focusStyle.normal.textColor = Color.red;
                GUI.Label(new Rect(20, y, 380, 20), "⬆ CLICK THE GAME VIEW TO PLAY ⬆", focusStyle);
            }
        }

        private void DumpHand()
        {
            PlayerManager active = GetActivePlayer();
            Debug.Log($"[Hand] {active.playerName} ({active.hand.Count} cards, WP: {active.willpowerPool}/{active.EffectiveWillpowerMax}):");
            for (int i = 0; i < active.hand.Count; i++)
            {
                var c = active.hand[i];
                Debug.Log($"  [{i + 1}] {c.DisplayName}  Cost: {c.cost} WP  Type: {c.cardType}");
            }
        }

        private void DumpBoard()
        {
            Debug.Log("[Board] ========================================");
            Debug.Log($"[Board] Active: {GetActivePlayer().playerName}  Phase: {currentPhase}");
            Debug.Log($"[Board] Influence: FP {fpPlayer.influence}  Shadow {shadowPlayer.influence}");
            Debug.Log($"[Board] Ring: {ring.GetCorruptionStatus()}");

            for (int i = 0; i < board.locations.Count; i++)
            {
                var loc = board.locations[i];
                string locName = loc.IsEmpty ? "Empty" : loc.locationCard.cardName;
                string ctrl = loc.IsEmpty ? "-" : (loc.controller == "fp" ? "FP" : "Shadow");
                string def = loc.IsEmpty ? "-" : $"{loc.currentDefense}";
                Debug.Log($"[Board] Loc {i + 1}: {locName} ({ctrl}) Def:{def}");

                var fpFront = loc.GetFrontLine("fp");
                var fpBack = loc.GetBackLine("fp");
                var shFront = loc.GetFrontLine("shadow");
                var shBack = loc.GetBackLine("shadow");

                foreach (var a in fpFront)
                    Debug.Log($"  FP Front: {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness} Pwr:{a.EffectivePower}){(a.tapped ? " [TAPPED]" : "")}");
                foreach (var a in fpBack)
                    Debug.Log($"  FP Back:  {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness} Pwr:{a.EffectivePower}){(a.tapped ? " [TAPPED]" : "")}");
                foreach (var a in shFront)
                    Debug.Log($"  SH Front: {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness} Pwr:{a.EffectivePower}){(a.tapped ? " [TAPPED]" : "")}");
                foreach (var a in shBack)
                    Debug.Log($"  SH Back:  {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness} Pwr:{a.EffectivePower}){(a.tapped ? " [TAPPED]" : "")}");
            }

            // Deployment zones
            Debug.Log("[Board] --- Deployment ---");
            foreach (var a in board.fpDeployment)
                Debug.Log($"  FP: {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness}){(a.tapped ? " [TAPPED]" : "")}");
            foreach (var a in board.shadowDeployment)
                Debug.Log($"  SH: {a.card.cardName} (Tgh:{a.currentToughness}/{a.card.toughness}){(a.tapped ? " [TAPPED]" : "")}");

            // Heroes
            if (fpPlayer.hero != null)
                Debug.Log($"[Board] FP Hero: {fpPlayer.hero.card.cardName} (Tgh:{fpPlayer.hero.currentToughness}/{fpPlayer.hero.card.toughness}){(fpPlayer.hero.tapped ? " [TAPPED]" : "")}");
            if (shadowPlayer.hero != null)
                Debug.Log($"[Board] SH Hero: {shadowPlayer.hero.card.cardName} (Tgh:{shadowPlayer.hero.currentToughness}/{shadowPlayer.hero.card.toughness}){(shadowPlayer.hero.tapped ? " [TAPPED]" : "")}");
            Debug.Log("[Board] ========================================");
        }

        // --- Card Play Input ---

        private void PlayCardFromHand(int index)
        {
            if (currentPhase != GamePhase.Main)
            {
                Debug.Log("[Input] Can only play cards during Main phase.");
                return;
            }

            PlayerManager active = GetActivePlayer();
            if (index < 0 || index >= active.hand.Count)
            {
                Debug.Log($"[Input] Invalid card index {index + 1}. Hand has {active.hand.Count} cards. Press H to see hand.");
                return;
            }

            CardData card = active.hand[index];
            var results = PlayCard(card, activePlayer);
            foreach (var msg in results)
                Debug.Log($"[PlayCard] {msg}");

            // If card was an ally, show board
            if (card.cardType == CardType.Ally)
                DumpBoard();
        }

        // --- Attack Input ---

        private void EnterAttackMode()
        {
            if (currentPhase != GamePhase.Main)
            {
                Debug.Log("[Input] Can only attack during Main phase.");
                return;
            }

            availableAttackers.Clear();
            string enemyId = activePlayer == "fp" ? "shadow" : "fp";

            // Collect all untapped allies at locations that have enemy targets
            for (int locIdx = 0; locIdx < board.locations.Count; locIdx++)
            {
                var loc = board.locations[locIdx];
                var enemies = loc.GetAllies(enemyId);
                if (enemies.Count == 0 && (loc.IsEmpty || loc.controller == activePlayer))
                    continue; // no one to attack here

                foreach (var ally in loc.GetAllies(activePlayer))
                {
                    if (!ally.tapped && !ally.hasAttackedThisTurn)
                        availableAttackers.Add(ally);
                }
            }

            // Include hero if at a location
            PlayerManager active = GetActivePlayer();
            if (active.hero != null && active.hero.IsAlive && !active.hero.tapped && !active.hero.hasAttackedThisTurn)
            {
                int? heroLoc = board.FindAllyLocation(active.hero, activePlayer);
                if (heroLoc != null && heroLoc >= 0)
                    availableAttackers.Add(active.hero);
            }

            if (availableAttackers.Count == 0)
            {
                Debug.Log("[Attack] No available attackers. Move allies to locations first.");
                return;
            }

            inputMode = InputMode.Attacking;
            Debug.Log($"[Attack] Select attacker (1-{availableAttackers.Count}):");
            for (int i = 0; i < availableAttackers.Count; i++)
            {
                var a = availableAttackers[i];
                int? atLoc = board.FindAllyLocation(a, activePlayer);
                string locStr = atLoc >= 0 ? $"Loc {atLoc.Value + 1}" : "Dep";
                Debug.Log($"  [{i + 1}] {a.card.cardName} ({locStr})  Pwr:{a.EffectivePower}  Tgh:{a.currentToughness}");
            }
            Debug.Log("[Attack] Esc to cancel.");
        }

        private void ExecuteAttack(BoardAlly attacker)
        {
            string enemyId = activePlayer == "fp" ? "shadow" : "fp";
            int? attackerLoc = board.FindAllyLocation(attacker, activePlayer);

            if (attackerLoc == null || attackerLoc < 0)
            {
                Debug.Log($"[Attack] {attacker.card.cardName} is not at a location. Move first.");
                return;
            }

            LocationSlot loc = board.GetLocation(attackerLoc.Value);
            var enemies = loc.GetAllies(enemyId);

            BoardAlly target = null;
            string targetType = "ally_front";

            // Prioritize front line enemies, then back line
            var frontEnemies = loc.GetFrontLine(enemyId);
            if (frontEnemies.Count > 0)
            {
                target = frontEnemies[0];
                targetType = "ally_front";
            }
            else
            {
                var backEnemies = loc.GetBackLine(enemyId);
                if (backEnemies.Count > 0)
                {
                    target = backEnemies[0];
                    targetType = "ally_back";
                }
                else if (!loc.IsEmpty && loc.controller != activePlayer)
                {
                    // Attack the location itself
                    var results = Attack(attacker, activePlayer, loc, "location");
                    foreach (var msg in results)
                        Debug.Log($"[Attack] {msg}");
                    return;
                }
                else
                {
                    Debug.Log($"[Attack] No valid targets at Location {attackerLoc.Value + 1}.");
                    return;
                }
            }

            Debug.Log($"[Attack] {attacker.card.cardName} → {target.card.cardName}!");
            var atkResults = Attack(attacker, activePlayer, target, targetType);
            foreach (var msg in atkResults)
                Debug.Log($"[Attack] {msg}");
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

            DumpPhase();
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

            DumpPhase();
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

                    // Resolve on-enter effects
                    var enterMsgs = effects.ResolveOnEnter(ally, player);
                    msgs.AddRange(enterMsgs);
                    break;

                case CardType.Event:
                    // Resolve event via EventResolver
                    var eventMsgs = events.ResolveEvent(card, player);
                    msgs.AddRange(eventMsgs);
                    playerState.discard.Add(card);
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

        // --- Combat ---

        /// <summary>
        /// Execute an attack. targetType can be "ally" or "location".
        /// Returns list of result messages.
        /// </summary>
        public List<string> Attack(BoardAlly attacker, string attackerPlayer,
            object target, string targetType)
        {
            var msgs = new List<string>();

            // Validate attacker can attack
            if (attacker.tapped || attacker.hasAttackedThisTurn)
            {
                msgs.Add($"{attacker.card.cardName} cannot attack (already acted this turn)!");
                return msgs;
            }

            // Execute combat
            var result = combat.ResolveAttack(attacker, attackerPlayer, target, targetType);
            msgs.AddRange(result.messages);

            // Cleanup destroyed ally
            if (result.targetDestroyed && targetType == "ally")
            {
                BoardAlly destroyed = target as BoardAlly;
                string destroyedPlayer = attackerPlayer == "fp" ? "shadow" : "fp";
                board.RemoveAlly(destroyed, destroyedPlayer);
                GetPlayerState(destroyedPlayer).discard.Add(destroyed.card);
                msgs.Add($"{destroyed.card.cardName} sent to discard.");
            }

            return msgs;
        }

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
